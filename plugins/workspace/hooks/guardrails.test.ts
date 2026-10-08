import { expect, test } from 'claude-code/testing'

import { evaluateGitCommand, looksLikeGitMutation, resolveRepoForCommand } from './guardrails'
import type { RepoInfo } from './model'

function repo(overrides: Partial<RepoInfo> = {}): RepoInfo {
  return {
    name: 'api',
    path: '/ws/api',
    branch: 'master',
    ahead: 0,
    behind: 0,
    dirtyCount: 0,
    isClean: true,
    defaultBranch: 'master',
    remotes: [
      { name: 'origin', url: 'u1', role: 'primary' },
      { name: 'upstream', url: 'u2', role: 'canonical' },
    ],
    worktrees: [],
    role: null,
    ...overrides,
  }
}

test('evaluateGitCommand: push to the canonical remote warns by default', async () => {
  const verdict = evaluateGitCommand('git push upstream main', repo(), 'warn')
  expect(verdict.action).toBe('warn')
})

test('evaluateGitCommand: push to the canonical remote denies under a deny posture', async () => {
  const verdict = evaluateGitCommand('git push upstream main', repo(), 'deny')
  expect(verdict.action).toBe('deny')
})

test('evaluateGitCommand: push to the primary remote is always fine', async () => {
  expect(evaluateGitCommand('git push origin feature-x', repo(), 'deny')).toEqual({ action: 'allow' })
})

test('evaluateGitCommand: a repo with no separate canonical remote never flags its push (two-node-toolbox case)', async () => {
  const soleRemoteRepo = repo({ remotes: [{ name: 'origin', url: 'u1', role: 'primary' }] })
  expect(evaluateGitCommand('git push origin main', soleRemoteRepo, 'deny')).toEqual({ action: 'allow' })
})

test('evaluateGitCommand: posture "off" always allows', async () => {
  expect(evaluateGitCommand('git push upstream main', repo(), 'off')).toEqual({ action: 'allow' })
})

test('evaluateGitCommand: committing on the default branch warns, never denies', async () => {
  const onDefault = repo({ branch: 'master', defaultBranch: 'master' })
  const verdict = evaluateGitCommand('git commit -m "wip"', onDefault, 'deny')
  expect(verdict.action).toBe('warn')
})

test('evaluateGitCommand: committing on a feature branch is fine', async () => {
  const onFeature = repo({ branch: 'feature-x', defaultBranch: 'master' })
  expect(evaluateGitCommand('git commit -m "wip"', onFeature, 'deny')).toEqual({ action: 'allow' })
})

test('resolveRepoForCommand matches a -C flag to the repo it names', async () => {
  const repos = [repo({ name: 'api', path: '/ws/api' }), repo({ name: 'oc', path: '/ws/oc' })]
  expect(resolveRepoForCommand('git -C /ws/oc status', repos)?.name).toBe('oc')
})

test('resolveRepoForCommand matches a leading cd', async () => {
  const repos = [repo({ name: 'api', path: '/ws/api' }), repo({ name: 'oc', path: '/ws/oc' })]
  expect(resolveRepoForCommand('cd /ws/api && git push', repos)?.name).toBe('api')
})

test('resolveRepoForCommand falls back to a bare path mention, and null when nothing matches', async () => {
  const repos = [repo({ name: 'api', path: '/ws/api' })]
  expect(resolveRepoForCommand('git --git-dir=/ws/api/.git log', repos)?.name).toBe('api')
  expect(resolveRepoForCommand('git status', repos)).toBeNull()
})

test('looksLikeGitMutation recognizes mutating subcommands and ignores read-only ones', async () => {
  expect(looksLikeGitMutation('git push origin main')).toBe(true)
  expect(looksLikeGitMutation('git worktree add -b x ../x')).toBe(true)
  expect(looksLikeGitMutation('git status')).toBe(false)
  expect(looksLikeGitMutation('git log --oneline')).toBe(false)
})
