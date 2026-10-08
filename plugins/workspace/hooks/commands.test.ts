import { expect, test } from 'claude-code/testing'

import { MIN_PANE_COLUMNS, paneFitsTerminal, parseWorkspaceCommandArg } from './commands'

test('parseWorkspaceCommandArg: no args opens the pane', async () => {
  expect(parseWorkspaceCommandArg('')).toBe('open')
  expect(parseWorkspaceCommandArg('   ')).toBe('open')
})

test('parseWorkspaceCommandArg: recognizes refresh and sync-doc', async () => {
  expect(parseWorkspaceCommandArg('refresh')).toBe('refresh')
  expect(parseWorkspaceCommandArg(' sync-doc ')).toBe('sync-doc')
})

test('parseWorkspaceCommandArg: an unknown argument falls back to opening the pane', async () => {
  expect(parseWorkspaceCommandArg('bogus')).toBe('open')
})

test('paneFitsTerminal: fullscreen needs the dock width, the main screen always fits', async () => {
  expect(paneFitsTerminal({ isFullscreen: true, columns: MIN_PANE_COLUMNS })).toBe(true)
  expect(paneFitsTerminal({ isFullscreen: true, columns: MIN_PANE_COLUMNS - 1 })).toBe(false)
  expect(paneFitsTerminal({ isFullscreen: false, columns: 60 })).toBe(true)
})
