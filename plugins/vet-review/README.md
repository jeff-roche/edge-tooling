# vet-review

Skeptical second pass on PR review findings — filters noise and validates real issues one by one.

## Installation

Install via Claude Code's plugin system:

```text
/plugin marketplace add openshift-eng/edge-tooling
/plugin install vet-review
```

## Usage

Run a review first, then vet the results:

```text
/review-pr 123
/vet-review
```

Or vet review comments already on a PR:

```text
/vet-review 123
```

Claude will:

1. Collect findings from the prior review (conversation context or PR comments)
2. Read surrounding code for each finding
3. Apply the "would a senior engineer flag this?" filter
4. Present surviving findings one-by-one for accept/discard/discuss
5. Report what was dropped and why

### When to use

- After running `/review-pr` and getting a list of findings
- After receiving an automated review (CodeRabbit, etc.) on a PR
- When you want a second opinion on review comments before acting on them

### What you get

- **Interactive vetting**: findings presented one at a time, you decide accept/discard/discuss
- **Noise filtering**: stylistic nits, impossible-case handling, and theoretical improvements are dropped with explanations
- **Dropped findings table**: transparency about what was filtered and why
- **Final tally**: summary of accepted, discarded, and dropped findings

## Requirements

- **Claude Code:** >= 1.0.0
- **Category:** debug

## Author

fonta-rh
