# Edge Payload Monitor

Automated monitoring tool for OpenShift nightly payload health across edge topologies (SNO, TNA, TNF). Fetches data from the amd64 release controller, Sippy Component Readiness, Prow CI, and JIRA to produce an interactive HTML dashboard.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with defaults (auto-discovers active OCP streams)
python -m payload_monitor

# Run and open report in browser
python -m payload_monitor --open

# Override versions
python -m payload_monitor --versions 4.18,4.19,4.20,4.21,4.22,4.23

# Patch AI analysis into an existing HTML report
python -m payload_monitor --merge-analysis reports/analysis-2026-03-25.json --output reports/report-2026-03-25.html
```

Or use the convenience wrapper:

```bash
./payload-monitor.sh
```

## What It Does

1. **Fetches nightly payloads** from the [amd64 release controller](https://amd64.ocp.releases.ci.openshift.org) for active OCP nightly streams (auto-discovered from both Sippy and the release controller, currently 4.18 through 5.0)
2. **Filters for edge topology jobs** (SNO, TNA, TNF) in blocking and informing job results
3. **Analyzes failures** by fetching Prow job logs and extracting failing test names and error signatures
4. **Queries Sippy** for job-level regressions (pass rate drops) across edge topologies
5. **Queries Component Readiness** for statistically significant regressions on Single Node vs HA topology
6. **Searches JIRA** for existing bugs matching failure signatures
7. **Generates an HTML dashboard** with health summaries, failure details, regressions, and JIRA integration

## Architecture

```
                    +-------------------+
                    |   CLI / Skill     |
                    +--------+----------+
                             |
                    +--------v----------+
                    |   Analyzer        |
                    +--------+----------+
                             |
     +------------+----------+----------+------------+
     |            |          |          |             |
+----v-------+ +--v------+ +v--------+ +v----------+ +v-----------+
| Release    | | Sippy   | | Comp.   | | JIRA      | | Prow       |
| Controller | | Jobs    | | Ready.  | | Collector | | Collector  |
+----+-------+ +---------+ +---------+ +-----------+ +-----+------+
     |                                                      |
     +------------------------------------------------------+
                             |
                    +--------v----------+
                    |  HTML Dashboard   |
                    +-------------------+
```

### Usage

**Standalone CLI**: Run `python -m payload_monitor` to collect data and generate an HTML dashboard.

**Claude Code skill**: Run `/edge-payload-monitor` to also get AI-powered root cause analysis for blocking job failures, using marketplace CI skills from [ai-helpers](https://github.com/openshift-eng/ai-helpers).

### Performance and Token Efficiency

- **Parallel data collection**: Release Controller, Sippy, and Component Readiness APIs are queried concurrently. Per-stream payload fetches are also parallelized.
- **Shared HTTP sessions**: All collectors reuse persistent connections with automatic retry and exponential backoff for transient failures.
- **No JSON round-trip**: AI analysis is patched directly into the existing HTML report instead of serializing/deserializing the full report data through JSON.
- **Minimal AI input**: Only a small `blocking.json` (job names and prow URLs) is read by Claude — never the full report data. Deep analysis runs only on blocking job failures; informing jobs get a lightweight Claude suggestion instead.
- **Multi-agent parallelism**: When multiple blocking jobs need analysis, each is analyzed by a separate subagent in parallel.

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
versions:
  auto_discover: true       # auto-discover active nightly streams
  override: []              # or specify: ["4.18", "4.19", "4.20", "4.21", "4.22", "4.23", "5.0"]

topologies:
  - name: SNO
    job_patterns: ["sno", "single-node", "metal-single-node"]
    exclude_patterns: ["telco"]
  - name: TNA
    job_patterns: ["two-node", "tna"]
    exclude_patterns: ["telco"]
  - name: TNF
    job_patterns: ["tnf", "two-node-fencing"]
    exclude_patterns: ["telco"]

payloads_per_stream: 5      # recent payloads to analyze per stream

jira:
  project: "OCPBUGS"
  component: "Edge Enablement"

output:
  report_dir: "./reports"

slack:                       # future feature
  webhook_url: ""
  channel: "#edge-enablement-payload-manager"
  enabled: false
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_TOKEN` | For JIRA features | Personal access token for issues.redhat.com |

To obtain a JIRA token, go to your [JIRA Personal Access Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) page and create a new token.

Set it in your shell before running:

```bash
export JIRA_TOKEN="your-token-here"
```

Or add it to `~/.bashrc` / `~/.zshrc` for persistence.

## CLI Reference

```
Usage: python -m payload_monitor [OPTIONS]

Options:
  --config PATH        Config file path (default: config.yaml)
  --versions TEXT      Override versions, comma-separated (e.g., "4.18,4.19")
  --output PATH        Output HTML file path (default: reports/report-YYYY-MM-DD.html)
  --from-json PATH     Regenerate HTML from a JSON file (skips data collection)
  --json               Also export full report data as JSON
  --merge-analysis PATH  Patch analysis JSON into an existing HTML report (or into --from-json data)
  --open               Open report in browser after generation
  --skip-prow          Skip Prow artifact fetching (faster, less detail)
  --skip-sippy         Skip Sippy regression check
  --verbose            Enable verbose logging
  --help               Show this message and exit
```

## Data Sources

| Source | API | Auth | Purpose |
|--------|-----|------|---------|
| [Release Controller](https://amd64.ocp.releases.ci.openshift.org) | `/api/v1/releasestream/*/tags` | None | Payload status, blocking/informing job results |
| [Sippy](https://sippy.dptools.openshift.org) | `/api/releases`, `/api/jobs` | None | Version auto-discovery, job pass rates, regressions |
| [Sippy Component Readiness](https://sippy.dptools.openshift.org/sippy-ng/component_readiness/main) | `/api/component_readiness` | None | HA vs Single Node topology regression detection |
| [Prow](https://prow.ci.openshift.org) | Job API + GCS artifacts | None | Job logs, junit XMLs, failing test details |
| [JIRA](https://issues.redhat.com) | REST API v2 | Token | Existing bug search, bug creation links |

## Topology Job Patterns

Jobs are classified by topology based on name patterns:

- **SNO** (Single Node OpenShift): `sno`, `single-node`, `metal-single-node`
- **TNA** (Two Node Active): `two-node`, `tna`
- **TNF** (Two Nodes with Fencing): `tnf`, `two-node-fencing`

These patterns are configurable in `config.yaml`.

## Dashboard Features

The generated HTML report is a single self-contained file (no external dependencies) with:

- **Version health status**: Per-version health indicator with payload acceptance timeline
- **Findings summary**: Actionable summary with suggested next steps
- **Failing edge jobs**: Blocking and informing job failures across SNO/TNA/TNF topologies
- **Failure analysis**: Error messages, failing tests, and AI root cause analysis (when enriched via Claude skill)
- **Sippy job regressions**: Edge jobs with significant pass rate drops compared to previous periods
- **Component Readiness**: HA vs Single Node topology regressions detected by Fisher's exact test
- **JIRA integration**: Matching existing bugs and suggested new bugs with pre-filled create links

## Scheduling

### Cron (daily at 6:00 AM UTC)

```bash
0 6 * * * cd /path/to/payload-monitor && python -m payload_monitor --output reports/daily-$(date +\%Y-\%m-\%d).html
```

### Claude Code (manual)

```
/edge-payload-monitor
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run with verbose output
python -m payload_monitor --verbose
```

## Future Roadmap

- Slack notifications to `@edge-enablement-payload-manager` with daily report summary
- Web portal integration (serve reports via simple HTTP server)
- Historical trend database (SQLite) for cross-day analysis
