import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Printer, Receipt } from '../types'

const WIDTH = 40
const TICK_MS = 130
const printer = atom(
  { plugin: 'scope-creep-receipt', key: 'printer' } as const,
  { receipt: null, shown: 0, isHidden: false } as Printer,
)

const READ_TOOLS = new Set(['Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch'])
const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit'])

type Row = { text: string; color?: string; bold?: boolean; dim?: boolean }

const dots = (label: string, value: string) =>
  label + ' ' + '.'.repeat(Math.max(2, WIDTH - label.length - value.length - 2)) + ' ' + value

const center = (text: string) =>
  ' '.repeat(Math.max(0, Math.floor((WIDTH - text.length) / 2))) + text

const clip = (text: string, max: number) =>
  text.length > max ? text.slice(0, max - 1) + '…' : text

const barcode = (seed: number) => {
  const glyphs = '▏▎▍▌▋▊▉█ ▕'
  let n = seed * 2654435761 + 12345
  let out = ''
  for (let i = 0; i < 30; i += 1) {
    n = (n * 1103515245 + 12345) & 0x7fffffff
    out += glyphs[n % glyphs.length]
  }
  return out
}

const short = (n: number) => (n >= 1000 ? `${+(n / 1000).toFixed(1)}k` : String(n))

const verdict = (touched: number): [string, string] => {
  if (touched < 4) return ['EXACTLY WHAT YOU ASKED', 'suspicious. who is this.']
  if (touched < 10) return ['A LITTLE EXTRA', 'it slipped its mind 9 times']
  if (touched < 25) return ['SCOPE CREEP: ENABLED', '3 guilt loops, 1 unresolved wound']
  return ['FULL ANXIETY COSPLAY', '43 tabs open. it is fine.']
}

const rowsFor = (r: Receipt): Row[] => {
  const touched = r.reads + r.edits + r.commands
  const [stamp, aside] = verdict(touched)

  return [
    { text: 'v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^', dim: true },
    { text: center('DEPT. OF ONE SMALL THING'), bold: true, color: 'yellow' },
    { text: center(`receipt #${String(r.no).padStart(4, '0')}`), dim: true },
    { text: '-'.repeat(WIDTH), dim: true },
    { text: dots('YOU ASKED FOR', `"${clip(r.asked, 14)}"`) },
    { text: dots('tabs opened "just to check"', String(r.reads)), color: 'cyan' },
    { text: dots('side quests started', String(r.edits)), color: 'magenta' },
    { text: dots('things run on a hunch', String(r.commands)), color: 'blue' },
    { text: dots('min of vibing in limbo', (r.seconds / 60).toFixed(1)) },
    { text: dots('tokens spent on intention', short(r.tokens)) },
    { text: '-'.repeat(WIDTH), dim: true },
    { text: dots('TOTAL', '1 thing (allegedly)'), bold: true },
    { text: center(`*** ${stamp} ***`), bold: true, color: touched < 4 ? 'green' : touched < 25 ? 'yellow' : 'red' },
    { text: center(aside), dim: true },
    { text: center('tip not included. refunds: later'), dim: true },
    { text: center('thank you for vibing'), dim: true },
    { text: center(barcode(touched + r.tokens + r.no)), dim: true },
    { text: '^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v', dim: true },
  ]
}

const DEMO: Receipt = {
  asked: 'fix one typo',
  reads: 43,
  edits: 17,
  commands: 9,
  seconds: 252,
  tokens: 312000,
  no: 42,
}

let stop: (() => void) | null = null

function printReceipt($: any, receipt: Receipt) {
  stop?.()
  const total = rowsFor(receipt).length
  void update($, printer, () => ({ receipt, shown: 0, isHidden: false }))
  const timer = $.clock.every(TICK_MS, async () => {
    const state = await read($, printer)
    if (state.shown >= total) {
      timer.cancel?.()
      return
    }
    await update($, printer, p => ({ ...p, shown: p.shown + 1 }))
  })
  stop = () => timer.cancel?.()
}

export const register: Register = on => {
  let startedAt = 0
  let asked = ''
  let reads = 0
  let edits = 0
  let commands = 0
  let lastTokens = 0
  let count = 0

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'receipt', description: 'Reprint the last receipt, or /receipt demo for a joke one' })

    return next(e)
  })

  on('command.run', { command: 'receipt' }, async ($, e) => {
    if (e.args.trim() === 'demo') {
      printReceipt($, DEMO)

      return { text: 'Printing a very honest receipt…' }
    }

    const { receipt } = await read($, printer)
    if (!receipt) return { text: 'Nothing to print yet. Try /receipt demo' }
    printReceipt($, receipt)

    return { text: 'Printing…' }
  })

  on('prompt.submit', async ($, e, next) => {
    startedAt = await $.clock.now()
    asked = String(e.text ?? '').replace(/\s+/g, ' ').trim()
    reads = 0
    edits = 0
    commands = 0

    return next(e)
  })

  on('tool.call', ($, e, next) => {
    if (READ_TOOLS.has(e.tool)) reads += 1
    else if (EDIT_TOOLS.has(e.tool)) edits += 1
    else if (e.tool === 'Bash') commands += 1

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)

    if (!e.agentId && asked !== '') {
      const { context } = await $.session.usage()
      const used = context?.tokens ?? 0
      const tokens = Math.max(0, used - lastTokens)
      lastTokens = used
      count += 1
      const seconds = Math.round(((await $.clock.now()) - startedAt) / 1000)
      printReceipt($, { asked, reads, edits, commands, seconds, tokens, no: count })
    }

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const p = await read($, printer)

    if (e.props.hasSurvey || p.receipt === null || p.isHidden || e.props.bodyColumns < WIDTH + 4) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const rows = rowsFor(p.receipt).slice(0, p.shown)
    const isDone = p.shown >= rowsFor(p.receipt).length

    return (
      <Box flexDirection="column" paddingX={1}>
        {rows.map((row, i) => (
          <Text key={`r${i}`} color={row.color} bold={row.bold} dimColor={row.dim}>
            {row.text}
          </Text>
        ))}
        {isDone ? (
          <Button key="tear" label="tear off" onPress={() => update($, printer, x => ({ ...x, isHidden: true }))} />
        ) : null}
      </Box>
    )
  })
}
