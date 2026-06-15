# MicroShift CI Artifact Primer

Reference for analyzing MicroShift Prow job artifacts. Read this when
unfamiliar with the artifact layout — it answers "which file answers
which question".

## Job types

- **Scenario-based e2e jobs** (`e2e-aws-tests-*`): the
  `openshift-microshift-e2e-metal-tests` step boots ~20 VM-based test
  scenarios on a hypervisor host. Failures are per-scenario; "the job
  failed" usually means 1–3 scenarios failed.
- **Direct-test jobs** (`*-ocp-conformance-*`, `e2e-aws-ai-model-serving-nightly`,
  `e2e-aws-footprint-and-performance-*`): run their test suite directly,
  no scenario fan-out. Job history IS the test history for these.

## Scenario naming

Scenario names encode OS image, MicroShift version source, and suite:

- `el96-lrel@standard1` — RHEL 9.6, latest release build, standard suite 1
- `el94-y2@el96-lrel@standard1` — upgrade chain: RHEL 9.4 + 2-year-old
  MicroShift upgraded to RHEL 9.6 latest, then standard suite 1
- Suite tokens: `standard1`/`standard2`, `lvm`, `dual-stack`, `ipv6`,
  `multi-nic`, `low-latency`, `ginkgo-tests`, `ai-model-serving-online`,
  `osconfig`, `storage`, `tlsv13-*`, `multi-config-*`

Scenario definitions (what each one deploys and runs) live in
openshift/microshift under `test/scenarios*/` (e.g. `test/scenarios-bootc/el9/`);
Robot Framework suites under `test/suites/`.

## Where the evidence lives

Per scenario, under
`artifacts/<TEST_NAME>/openshift-microshift-e2e-metal-tests/artifacts/scenario-info/<scenario>/`:

| File | Answers |
| ---- | ------- |
| `junit.xml` | Which tests failed; the top-level `testsuite name` IS the scenario name |
| `rf-debug.log` | Robot Framework execution trace with timestamps — failures marked `\| FAIL \|`; the primary test-failure evidence |
| `boot_and_run.log` | VM boot + scenario orchestration; timeouts killing the whole scenario show up here (`timeout: sending signal TERM`) |
| `phase_*/` | Per-phase logs (create, run, teardown) |
| `vms/host1/sos/journal_*.log` | **Plain-text journal exports** — readable without extracting anything; check these FIRST for service failures, x509 errors, OOM kills |
| `vms/host1/sos/sosreport-*.tar.xz` | Full sosreports (see below) |

## Sosreports

- The sos-on-failure listener (`test/resources/sos-on-failure-listener.py`
  in openshift/microshift) captures a sosreport **at each test failure**,
  in addition to the end-of-scenario one. **Prefer the on-failure
  report**: it still contains the pods and container logs of the
  namespaces created for that test, which the end-of-scenario report
  lacks (already cleaned up). Match report to failure by capture time.
- Extract with `bash plugins/microshift-ci/scripts/extract-sosreport.sh <dir>`
  and read its JSON index (journals, namespace pod logs, pre-grepped
  highlights).
- Inside an extracted report:
  - MicroShift journal: `sos_commands/microshift/journalctl_--no-pager_--unit_microshift`
  - Per-namespace pod logs:
    `sos_commands/microshift/namespaces/<ns>/pods/<pod>/<container>/<container>/logs/current.log`
    — and `previous.log` when the container was restarted. **The tail of
    `previous.log` states why the container died** (fatal error, leader
    election lost, panic).

## Reading the journal for component failures

Reconstruct a timestamped component timeline before attributing fault:

- Pod lifecycle: kubelet `SyncLoop (PLEG)` events, `Created container` /
  `Started container` (crio), `SyncLoop (probe)` readiness transitions,
  `prober.go "Probe failed"` lines.
- **Two `Created container` events for the same pod = the first instance
  died and was restarted** — a single startup narrative is wrong; read
  `previous.log` for the exit reason.
- Greenboot: `40_microshift_running_check.sh` lines show which
  deployments it waited for and when each became ready; the final
  verdict is `greenboot[...]: Script '40_microshift_running_check.sh' SUCCESS/FAILURE`.
- etcd pressure: `apply request took too long` warnings indicate
  apiserver/etcd latency (can cost components their leader-election
  leases).

## Timeouts that masquerade as test failures

The metal-tests step wraps Robot Framework in
`timeout -v --kill-after=5m 30m` per scenario (`TEST_EXECUTION_TIMEOUT`).
When the suite total exceeds it, the current test dies with
`Execution terminated by signal` and every subsequent test reports
`Test execution stopped due to a fatal error` — a cascade with ONE root
cause (the time budget), not independent failures.

## Search/index coverage of external tools

- Sippy tracks these jobs at **job level only** — scenario junits and RF
  suite names are not ingested.
- Search.CI indexes build logs and junit, **not** scenario-internal logs
  (`rf-debug.log` content is not searchable).
