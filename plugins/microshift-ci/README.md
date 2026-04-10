# microshift-ci

Analyze MicroShift CI failures, produce HTML reports, and create JIRA bugs.

## Installation

```text
/plugin marketplace add openshift-eng/edge-tooling
/plugin install microshift-ci
```

## Skills

| Skill | Description |
|---|---|
| `/doctor` | Analyze CI for multiple releases and produce an HTML summary |
| `/prow-job` | Root cause analysis of a single Prow job |
| `/test-job` | Comprehensive job metadata and scenario results |
| `/test-scenario` | Analyze individual test scenario results |
| `/create-bugs` | Search JIRA for duplicates and create bugs (dry-run by default) |

## Usage

### Full pipeline
```text
/doctor 4.19,4.20,4.21,4.22
```

### Single job analysis
```text
/prow-job https://prow.ci.openshift.org/view/gs/test-platform-results/logs/<job-name>/<job-id>
```

### Create bugs from analysis
```text
/create-bugs 4.22           # dry-run
/create-bugs 4.22 --create  # interactive creation
```

## Requirements

- `gcloud` CLI (authenticated for GCS access)
- `gh` CLI (authenticated with access to openshift/microshift)
- Jira MCP server configured (for bug correlation)
- Python 3
- **Category:** ci-cd

## Author

ggiguash
