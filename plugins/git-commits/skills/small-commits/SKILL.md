---
name: small-commits
description: "Create small, well-structured git commits that tell a coherent implementation story. Use when the user says: small commits, clean commits, good git history, logical commits, commit in small pieces, split commits, atomic commits, granular commits, structured commits, commit story, clean history. Not for PR creation."
user-invocable: true
allowed-tools: Bash, Read, Write
---

# small-commits

Structure uncommitted changes into small, logical git commits. Each
commit represents one coherent idea — a single function, a config
change, a test, a refactor step. The git log reads like a story of
how the implementation was built.

## Prerequisites

Run `git status` to confirm there are uncommitted changes. If the
current branch is `main` or `master`, warn the user and ask to confirm
before proceeding.

## Steps

### 1. Survey the Changes

Run in parallel:

```bash
git status
git diff --stat
git diff --cached --stat
git log --oneline -10
```

Read the full diff to understand what changed:

```bash
git diff
git diff --cached
```

For untracked files, read their contents with the Read tool.

### 2. Plan the Commit Sequence

Group changes into logical commits. Each commit must be:

- **One idea**: a function, a fix, a config change, a test, a rename
- **Buildable**: the repo is not broken after this commit
- **Ordered**: dependencies come first (add utility before the code
  that calls it)

Present the plan to the user:

```text
## Proposed Commit Plan

1. Add helper function `parseConfig` in utils.go
2. Refactor `main()` to use `parseConfig`
3. Add unit tests for `parseConfig`
4. Update README with new config format
```

Wait for the user to confirm or adjust before proceeding.

### 3. Stage and Commit Each Piece

For each planned commit, stage ONLY the changes that belong to it.

**Case A — Entire file belongs to this commit:**

```bash
git add path/to/file.go path/to/other.go
```

**Case B — File has changes spanning multiple commits:**

Use the patch-file technique to stage specific hunks:

1. Generate the diff:

   ```bash
   git diff path/to/file.go > /tmp/full.patch
   ```

2. Read the patch. Identify hunk boundaries — lines starting with
   `@@`. Each hunk header looks like:
   `@@ -start,count +start,count @@ context`

3. Write a partial patch containing ONLY the hunks for this commit.
   The partial patch MUST include:
   - The diff header lines (`diff --git a/... b/...`, `index ...`,
     `--- a/...`, `+++ b/...`)
   - Only the `@@` hunk(s) that belong to this commit

4. Apply the partial patch to the index:

   ```bash
   git apply --cached /tmp/partial.patch
   ```

5. Verify what got staged:

   ```bash
   git diff --cached path/to/file.go
   ```

6. If the staged diff does not match expectations, unstage and retry:

   ```bash
   git reset HEAD path/to/file.go
   ```

**Case C — New untracked file:**

```bash
git add path/to/new-file.go
```

**Committing:**

After staging, create the commit. Follow the user's existing commit
message conventions. Check `git log --oneline -5` for style reference.

Commit message rules:

- Subject line: imperative mood, max 72 chars, no trailing period
- Body (optional): explain WHY, not WHAT — the diff shows what

### 4. Handle Fixups to Earlier Commits

If while working through the plan you find a change that logically
belongs to an earlier commit on the branch, use fixup:

1. Find the target commit:

   ```bash
   git log --oneline -20
   ```

2. Create a fixup commit:

   ```bash
   git add <relevant-files>
   git commit --fixup=<target-sha>
   ```

   This creates a NEW commit with the message `fixup! <original subject>`.
   It gets folded into the target during autosquash.

### 5. Final Autosquash (optional)

After all commits are made, if fixup commits exist on the branch,
offer to fold them:

```text
There are N fixup commits. Run `git rebase --autosquash` to fold them
into their targets?
```

If the user confirms:

```bash
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base-ref>
```

Where `<base-ref>` is the earliest commit that should be included in
the rebase. Determine it from `git log --oneline` — look for the
oldest fixup target. `GIT_SEQUENCE_EDITOR=true` makes the interactive
rebase non-interactive by accepting the auto-generated sequence as-is.

PR branches are personal and force-pushable — do not warn about
rewriting history on non-main branches. This follows the standard
rebase-and-force-push workflow used in Kubernetes and similar projects.

### 6. Show the Result

```bash
git log --oneline
```

## Gotchas

- **Do not use `git add -i` or `git add -p`**: The interactive flag is
  blocked. Always use the patch-file approach from Step 3 Case B.

- **Do not use `git commit --amend`**: Use `git commit --fixup=<sha>`
  instead. It creates a new commit that gets folded during autosquash.

- **Partial patches must preserve the diff header**: When splitting a
  diff, always include the full `diff --git a/... b/...`, `index ...`,
  `--- a/...`, `+++ b/...` header block. Without it, `git apply`
  rejects the patch.

- **Already-staged changes**: Check `git diff --cached --stat` first.
  If the user has already staged changes, incorporate them into the
  commit plan.

- **Binary files**: `git diff` does not produce patches for binary
  files. Stage them with `git add <file>` — they cannot be split.

- **Merge conflicts in rebase**: If autosquash hits a conflict, stop
  and tell the user. Do not attempt automatic conflict resolution
  during rebase.

## Examples

**User**: "I've made a bunch of changes, can you create small commits?"

Runs `git diff --stat`, identifies 5 changed files spanning 3 logical
changes, presents a 3-commit plan, stages and commits each piece,
shows the final log.

**User**: "Small commits please" (mid-conversation after making changes)

Auto-invokes this skill, surveys changes, proposes a commit plan, asks
for confirmation, executes.

**User**: `/small-commits`

Explicit invocation — same workflow.
