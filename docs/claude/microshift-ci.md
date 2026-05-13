# MicroShift CI Plugin

## Installation

```text
/plugin marketplace add openshift-eng/edge-tooling
/plugin install microshift-ci
```

## What Runs in CI

A periodic Prow job (`periodic-ci-openshift-eng-edge-tooling-main-microshift-ci-doctor`)
runs daily and performs three phases automatically:

1. **Analysis** — `/microshift-ci:doctor 4.18,4.19,4.20,4.21,4.22,5.0,main`
   (50 min budget, 100 turns)
2. **Bug creation dry-run** — `/microshift-ci:create-bugs <releases>`
   (10 min budget, 50 turns)
3. **Rebase PR restart** — automatically restarts failed rebase bot PR tests

The job produces an HTML report, per-job analysis files, bug mapping JSON,
and a session archive for local continuation. All artifacts are available
in the Prow job's artifact directory.

## Daily Workflow

Start from the CI job results — don't re-run doctor locally.

### 1. Open the CI job

Find the latest run at:

```text
https://prow.ci.openshift.org/?job=periodic-ci-openshift-eng-edge-tooling-main-microshift-ci-doctor
```

Open the artifacts tab. The HTML report (`0-microshift-ci-doctor-report-summary.html`)
is the entry point — it shows all failures grouped by release with JIRA correlation.

### 2. Continue locally

Download the CI session artifacts into a local workdir:

```text
/microshift-ci:continue-session <prow-job-url>
```

This sets up the same workdir layout the CI job used, so all subsequent
commands work on the downloaded data.

### 3. Review bug candidates

```text
/microshift-ci:create-bugs 4.20,4.21,4.22,5.0,main --auto
```

Dry-run: shows what bugs would be created or skipped, with decisions
(duplicate, stale regression, infrastructure, or new).

### 4. Create bugs

```text
/microshift-ci:create-bugs 4.20,4.21,4.22,5.0,main --auto --create
```

Executes: creates JIRA bugs in USHIFT, skips duplicates and infrastructure failures.
Drop `--auto` for interactive per-candidate prompts.

### 5. Investigate specific failures

```text
/microshift-ci:prow-job <prow-url>
/microshift-ci:test-job <prow-url>
/microshift-ci:test-scenario <prow-url> <scenario-name>
```

- `prow-job` — root cause analysis of a single failed job
- `test-job` — comprehensive job metadata and all scenario results
- `test-scenario` — deep dive into one scenario's test results

### 6. Refresh report after changes

```text
/microshift-ci:doctor-refresh 4.20,4.21,4.22,5.0,main
```

Re-runs JIRA correlation and regenerates the HTML report from existing
job analysis files (does not re-analyze jobs).

## PR Job Management

The CI job automatically restarts failed rebase bot PR tests.
To run manually:

```bash
# Restart failed rebase PR jobs (dry-run)
bash plugins/microshift-ci/scripts/prow-jobs-for-pull-requests.sh \
  --mode restart --author 'microshift-rebase-script[bot]'

# Restart failed rebase PR jobs (execute)
bash plugins/microshift-ci/scripts/prow-jobs-for-pull-requests.sh \
  --mode restart --author 'microshift-rebase-script[bot]' --execute
```

## More Info

See the [plugin README](../../plugins/microshift-ci/README.md) for prerequisites,
full skill list, and usage examples.
