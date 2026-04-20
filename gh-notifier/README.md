# gh-notifier

Python script that lists **open pull requests** in configured GitHub repos, keeps only PRs whose **authors** appear in the team roster derived from **`OWNERS`** and **`OWNERS_ALIASES`**, applies **draft / label** filters, flags PRs that **need attention** (stale activity, age, optional label rules), and either posts a **Slack Block Kit** message or prints a text summary.

There are **no third-party packages** (stdlib only: `urllib`, `json`, etc.).

Design background and operational expectations: [`../proposals/gh-notifier.md`](../proposals/gh-notifier.md).

## Requirements

- **Python 3.11+** (recommended; matches other tooling in this repository)
- A **GitHub token** with permission to **read** pull requests on the repos you configure (`GITHUB_TOKEN`)
- Optional: **Slack Incoming Webhook** URL for channel posts (`SLACK_WEBHOOK_URL`)

## How it works (short)

1. Loads **`OWNERS`** and **`OWNERS_ALIASES`** from the **edge-tooling** repo root by default (the directory above `gh-notifier/`), unless you override paths with env vars.
2. Collects every raw entry under **`approvers:`** and **`reviewers:`** in `OWNERS`. Each entry is either an **alias** name defined under `aliases:` in `OWNERS_ALIASES` (expanded to GitHub logins) or treated as a **literal GitHub login**.
3. For each configured repo, fetches **open** PRs from the GitHub API, keeps **non-draft** PRs whose author is in that login set and that do not carry **excluded** labels.
4. Marks PRs **needing attention** when they are idle or old enough (`STALE_DAYS`), or when optional **required** / **forbidden** label rules fail.
5. If **`SLACK_WEBHOOK_URL`** is set, sends one Slack message; otherwise, if any PRs need attention, prints details to **stdout** (useful in CI logs).

## Run locally

From the **edge-tooling** repository root (so the default `OWNERS` paths resolve):

```bash
export GITHUB_TOKEN="ghp_..."           # required
export SLACK_WEBHOOK_URL="https://..."  # optional; omit to only print when there is work

python3 gh-notifier/gh-notifier.py
```

Run from another working directory only if you set **`OWNERS_FILE`** and **`OWNERS_ALIASES_FILE`** to absolute paths inside a checkout of this repo.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | yes | — | Bearer token for `api.github.com` |
| `SLACK_WEBHOOK_URL` | no | empty | If set, posts the dashboard to Slack; if unset, Slack is skipped |
| `OWNERS_FILE` | no | `<repo>/OWNERS` | Path to `OWNERS` (Kubernetes-style `approvers` / `reviewers`) |
| `OWNERS_ALIASES_FILE` | no | `<repo>/OWNERS_ALIASES` | Path to `OWNERS_ALIASES` (`aliases:` block) |
| `GITHUB_REPOS` | no | `openshift-eng/edge-tooling` | Comma- or whitespace-separated `org/repo` list |
| `STALE_DAYS` | no | `7` | Days of inactivity / age used for “needs attention” |
| `EXCLUDE_LABELS` | no | hold / WIP-style defaults | Comma or semicolon separated; PRs with any of these (case-insensitive) are skipped |
| `REQUIRED_LABELS` | no | empty | If set, PRs missing any of these labels are flagged |
| `FORBIDDEN_LABELS` | no | empty | If set, PRs carrying any of these labels are flagged |

`GITHUB_TOKEN`, `SLACK_WEBHOOK_URL`, and string list env vars are read **once at process start** (together with repo and label settings). `OWNERS` paths are resolved in `main()` after that.

## Slack payload

The message uses Slack **Block Kit** (header, context, sections). The number of PRs listed in one message is capped (`MAX_PRS_IN_MESSAGE` in the script).

## CI (openshift/release)

The intended integration is a **weekday periodic** job in **openshift/release** that checks out **edge-tooling** and runs this script with `GITHUB_TOKEN` and `SLACK_WEBHOOK_URL` supplied from CI secrets. Team membership stays in **`OWNERS`** / **`OWNERS_ALIASES`** in this repository, not duplicated in release.
