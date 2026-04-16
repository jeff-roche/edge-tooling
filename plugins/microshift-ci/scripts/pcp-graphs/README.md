# PCP Performance Graphs for MicroShift CI

Generate performance graphs from PCP (Performance Co-Pilot) archives
collected during MicroShift CI job runs. Produces disk I/O and CPU usage
charts that are embedded in the ci-doctor HTML report.

## Background

MicroShift CI jobs collect PCP archives via the `pcp-zeroconf` package
throughout the test run, capturing system-wide performance metrics at
high resolution. This tool processes those archives and produces
time-series graphs at 15-second intervals.

### Disk I/O Graph

Shows **Disk Read OPS**, **Disk Write OPS**, and **Disk Await** (ms).
Disk Await is the average time I/O requests spend waiting to be serviced.
When await rises above ~10 ms, etcd heartbeats can be missed. The tool
reports the max await across all block devices at each sample point.

### CPU Usage Graph

Shows **User** and **System** CPU usage as a stacked area chart (0-100%).
Useful for identifying CPU saturation during test runs.

## PCP Data Location in CI Artifacts

```text
artifacts/<test_name>/openshift-microshift-infra-pmlogs/artifacts/<ci_hostname>/
```

The directory contains files like `yyyymmdd.hh.mm.{0,index,meta}` and a
`Latest` folio file.

## Prerequisites

- `pcp-export-pcp2json` package (provides the `pcp2json` command)
- Python 3 with `matplotlib`

Install:
```bash
sudo dnf install -y pcp-export-pcp2json
pip install matplotlib
```

## Usage

Graphs are generated automatically by `doctor.sh graphs`:

```bash
bash doctor.sh graphs --workdir /tmp/microshift-ci-claude-workdir.YYMMDD
```

This finds all PCP archives in downloaded artifacts and produces PNG
graphs at `${WORKDIR}/graphs/<build_id>/`. The `finalize` step then
embeds them as base64 in the HTML report.

## Output

| File | Description |
|---|---|
| `disk_io.json` | Extracted data: `timestamps`, `bi` (reads/s), `bo` (writes/s), `await` (ms) |
| `disk_io.png` | Disk I/O chart with Read OPS (blue), Write OPS (red), Await (green dashed) |
| `cpu_usage.json` | Extracted data: `timestamps`, `user` (%), `sys` (%), `idle` (%) |
| `cpu_usage.png` | CPU usage stacked area chart: User (blue), System (red) |

## Files

| File | Purpose |
|---|---|
| `generate-graphs.sh` | Orchestrator: finds PCP archives, runs extraction and plotting in parallel |
| `extract_io.sh` | Runs `pcp2json` for disk metrics, pipes through `parse_pcp.py` |
| `extract_cpu.sh` | Runs `pcp2json` for CPU metrics, pipes through `parse_cpu.py` |
| `parse_pcp.py` | Parses pcp2json disk output, aggregates per-device (sum read/write, max await) |
| `parse_cpu.py` | Parses pcp2json CPU output, normalizes to percentages |
| `plot_io.py` | Generates disk I/O PNG from JSON data |
| `plot_cpu.py` | Generates CPU usage PNG from JSON data |

## Adding a New Graph Type

1. Create `extract_<type>.sh` and `parse_<type>.py` (follow existing patterns)
2. Create `plot_<type>.py`
3. Add a block to `generate-graphs.sh` to call them
4. No changes needed in `create-report.py` — it auto-discovers all `*.png` files
