import { describe, expect, test } from 'claude-code/testing'

describe('scope-creep-receipt', () => {
  test('prints a receipt after a turn', async ($, on) => {
    on('command.register', () => ({ value: { isRegistered: true } }) as any)
    on('clock.now', () => ({ value: 1000 }) as any)
    on('clock.every', () => ({ value: undefined }) as any)
    on('session.start', ($, e) => ({ cwd: e.cwd }))
    on('prompt.submit', ($, e) => ({ text: e.text }) as any)
    on('session.usage', () => ({ value: { startedAt: 0, rateLimits: [], context: { tokens: 5000, window: 200000, percent: 3 } } }))
    on('turn.complete', () => ({ text: '' }))
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' } as any)
    await $.prompt.submit({ text: 'fix one typo' } as any)
    await $.turn.complete({ reason: 'answer', answer: 'ok', durationMs: 1 } as any)
    const ui = await $.ui.mount({
      plugin: 'scope-creep-receipt',
      surface: 'terminal',
      component: 'AbovePrompt',
      props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 120 },
    } as any)
    expect(await ui.find({ type: 'Text', text: /CLAUDE CODE SUPPLY CO|v\^v\^/ })).toBeDefined()
    await ui.unmount()
  })
})
