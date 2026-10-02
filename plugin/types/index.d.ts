export type Receipt = {
  asked: string
  reads: number
  edits: number
  commands: number
  seconds: number
  tokens: number
  no: number
}

export type Printer = { receipt: Receipt | null; shown: number; isHidden: boolean }

declare module 'claude-code' {
  interface PluginState {
    'scope-creep-receipt': { printer: Printer }
  }
}
