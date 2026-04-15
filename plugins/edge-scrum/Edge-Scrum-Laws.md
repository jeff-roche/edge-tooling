# Edge Scrum Laws

Authoritative reference for AI agents and skills operating in the OpenShift Edge scrum environment. All process, Jira conventions, and team structure below is specific to the OpenShift Edge unified scrum.

---

## Team Roster

An issue belongs to the team if a roster member is the **assignee** or the **QA Contact** (`customfield_10470`). Exclude issues where neither field matches a roster member.

The roster is defined in `.roster.json` in the plugin directory (`plugins/edge-scrum/.roster.json`). This file is excluded from version control — copy `.roster.json.example` to `.roster.json` and populate it with your team. Agents and skills must read this file at runtime to determine team membership, per-member SP targets, and total capacity.

---

## Jira Configuration

### Projects

| Key | Purpose |
|---|---|
| `OCPEDGE` | Primary project: all team stories, bugs, spikes, tasks, and epics |
| `OCPBUGS` | Secondary bugs project; team owns: `Installer / Single Node OpenShift`, `Two Node with Arbiter`, `Two Node Fencing`, `Logical Volume Manager Storage` |
| `OCPSTRAT` | Features and Initiatives for the release cycle; use label `ocpedge-plan` and filter by projects: (`OCPEDGE`, `USHIFT`) |
| `USHIFT` | MicroShift feature and bug tracking (unified scrum target state; no dedicated scrum board) |

### Issue Hierarchy

```text
Stories / Spikes / Bugs / Tasks
  └── Epics  (linked via Epic Link field)
        └── Features / Initiatives  (linked via Parent Link field)
```

- Stories/Spikes/Bugs always link to an Epic via **Epic Link**.
- Epics link to a Feature or Initiative via **Parent Link** (recommended, not required).
- Stories without an epic are non-compliant.

### Issue Types

| Type | Purpose | Sizing | PR Required |
|---|---|---|---|
| **Story** | Capability delivery from the user's perspective | Story Points (fibonacci) | Yes |
| **Spike** | Time-boxed research; ends with written stories or a new spike | Story Points (fibonacci) | No |
| **Task** | Finite piece of work; post-meeting follow-ups, action items | Story Points (fibonacci) | No |
| **Bug** | Error, flaw, or fault in software | Always **0 SP** | Usually yes |
| **Epic** | Extra-large work bucket spanning multiple sprints | T-shirt size | N/A |
| **Feature** | Tangible value delivered to customers within a release | T-shirt size | N/A |
| **Initiative** | Architectural or improvement work; no direct customer deliverable | T-shirt size | N/A |

**Types NOT used by this team:** Ticket, Subtask (enabled but excluded from scrum functions).

### Story Pointing

Story points use the **fibonacci sequence**: 0, 1, 2, 3, 5, 8, 13.

Points represent the fraction of a sprint's capacity consumed by the work item:

| Points | Meaning |
|---|---|
| 0 | Trivial; entered for transparency (or any bug) |
| 1 | < 25% of sprint capacity |
| 2 | 25–40% of sprint capacity |
| 3 | 40–60% of sprint capacity |
| 5 | 60–90% of sprint capacity |
| 8 | 90%+ of sprint capacity |
| 13 | Full sprint of dedicated focus — likely too big; split or create an Epic |

**Rules:**

- All bugs are pointed at **0**. No exceptions.
- Pointed by the **assignee**.
- Target: **8 SP per team member per sprint** (acceptable range: 8–10).
- Repoint on assignee change if the new assignee's capacity differs.
- If a story's scope changes mid-sprint, repoint and leave a comment explaining why.

### Epic Sizing (T-shirt)

| Size | Expected Duration |
|---|---|
| XS | ~1 sprint (consider using a Story instead) |
| S | ~2 sprints |
| M | ~3 sprints |
| L | ~4 sprints |
| XL | ~5 sprints (likely too big; split or create a Feature/Initiative) |

### Feature / Initiative Sizing (T-shirt)

| Size | Expected Duration |
|---|---|
| XS | < 30% of release (~2 dev sprints) — consider using an Epic |
| S | 30–60% of release (~2–3 dev sprints) |
| M | 60–90% of release (~3–4 dev sprints) |
| L | 90%+ of release (~4+ dev sprints) |
| XL | Entire release (~5 full dev sprints) — likely too big; split or create an Outcome |

### Labels

All team labels use the `OCPEDGE:` namespace prefix.

| Label | Usage |
|---|---|
| `ocpedge-plan` | Apply to Outcome, Feature, or Epic. Recursively adds labeled work to the Jira Plan (backlog). |
| `ocpedge` | Apply at Epic and Story level. **Only needed for work outside the OCPEDGE project.** |
| `OCPEDGE:Docs` | Doc-specific tasks |
| `OCPEDGE:QE` | QE-specific tasks |
| `OCPEDGE:RHEL-Verification` | RHEL ticket verification tasks for TNF |
| `OCPEDGE:CI` | CI-affecting bugs; CI automation outside Payload Manager duties |
| `OCPEDGE:Payload-Manager` | Work done as part of Payload Manager duties |
| `OCPEDGE:Tooling` | Team tooling improvements (e.g., edge-tooling repo) |
| `OCPEDGE:Scrum` | Scrum process improvements or scrum-related automation |

### Components (Workstreams)

Components have a 1-to-1 correlation with workstreams. Use these exactly:

- `MicroShift`
- `Two Node with Arbiter`
- `Two Node with Fencing`
- `SNO`
- `Logical Volume Manager Storage`
- `Bandwidth Reduction`
- `Topology Transition` (covers MicroShift-to-SNO and Adaptable Topology)

Work outside these workstreams uses a scoped label instead of a component.

### Jira Filters (Target State)

| Filter | Type | Purpose |
|---|---|---|
| OpenShift Edge - Scrum Board | Core | Top-of-funnel; drives the scrum board |
| OpenShift Edge - Core Backlog | Core | All OCPEDGE and USHIFT backlog items |
| OpenShift Edge - External Projects | Core | Work in external Jira projects |
| OpenShift Edge - Bugs and CVEs | Core | Bugs and CVEs from OCPEDGE, USHIFT, OCPBUGS |
| OpenShift Edge - Team Assigned | Utility | Limits results to team members |
| OpenShift Edge - QE Assigned | Utility | Issues in QA state with a team member as QA contact |
| OpenShift Edge - Labels | Utility | Issues with any team-relevant label |
| OpenShift Edge - Components | Utility | Issues with any team-relevant component |
| OpenShift Edge Workstream - SNO | Utility | SNO-scoped issues |
| OpenShift Edge Workstream - TNA | Utility | Two Node Arbiter-scoped issues |
| OpenShift Edge Workstream - TNF | Utility | Two Node Fencing-scoped issues |
| OpenShift Edge Workstream - MicroShift | Utility | MicroShift-scoped issues |
| OpenShift Edge Workstream - LVMS | Utility | LVMS-scoped issues |
| OpenShift Edge Workstream - Adaptable Topology | Utility | NextGen Adaptable Topology issues |
| OpenShift Edge Workstream - MicroShift to SNO | Utility | NextGen MicroShift to SNO issues |
| OpenShift Edge Workstream - Bandwidth Reduction | Utility | Bandwidth Reduction issues |

### Custom Fields (Red Hat Jira Instance)

| Field | Custom Field ID | Type | Usage |
|---|---|---|---|
| Story Points | `customfield_10028` | Numeric | SP value for Stories, Tasks, Spikes |
| Epic Link | `customfield_10014` | Issue link | Story → Epic relationship |
| Parent Link | `customfield_10018` | Issue link | Epic → Feature/Initiative relationship |
| QA Contact | `customfield_10470` | User picker | QA owner for an issue |
| Flagged | `customfield_10021` | Array | Non-empty = impediment flag |
| Doc Contact | `customfield_10473` | User picker | Documentation owner for an issue |
| SME | `customfield_10475` | User picker | Subject Matter Expert for a Feature/Initiative |
| T-shirt Size | `customfield_10795` | String | Size (XS/S/M/L/XL) for Features and Initiatives |

---

## Workflow States

### Feature / Initiative States

| State | Meaning |
|---|---|
| New | Created; not yet committed work |
| Refinement | SME is investigating; refinement spike in progress |
| Backlog | Refinement complete; epics created; ready to be worked |
| In Progress | Active development underway |
| Dev Complete | All implementation PRs merged |
| Closed | Acceptance criteria met |

Features in **New** state are **not a commitment** of work.

### Epic States

| State | Meaning |
|---|---|
| Planning | Being refined; stories not yet created |
| To Do | Refinement done; ready for sprint planning |
| In Progress | Stories being actively worked |
| Dev Complete | All implementation PRs merged (docs/QE/CI stories may still be open) |
| Closed | All acceptance criteria met |

When an Epic transitions to **Dev Complete**, set the **Fix Version**. When transitioning to **In Progress**, set the **Target Version**. The **Epic Status** field must be set to **Done** when closed (handled by Jira automation).

### Story / Spike / Task States

| State | Meaning |
|---|---|
| To Do | Ready to be worked; in a sprint |
| In Progress | Actively being worked |
| Review | PR open; waiting for review/merge |
| Closed | Done; acceptance criteria met |

Bugs closed without story points are auto-set to 0 by automation.

### Bug States (OCPBUGS)

| State | Meaning |
|---|---|
| NEW | Reported; not yet triaged |
| ASSIGNED | Triaged; being actively worked (equivalent to In Progress) |
| MODIFIED | Fix merged; awaiting QA |
| ON_QA | In QA verification |
| Verified | QA confirmed fix |
| Closed | Complete |

**Note:** LVMS bugs do **not** automatically transition from MODIFIED to ON_QA via ART automation. Engineers must move LVMS bugs manually.

---

## Scrum Ceremonies

### Sprint Planning

**Preparation:**

1. Copy previous sprint review slides; update goal progress, highlights, and scrum report link.
2. Calculate sprint capacity: copy the capacity template, enter PTO/holidays per person.

**Agenda:**

1. Remind team to finalize Jira updates before sprint end.
2. Present previous sprint review slides.
3. End the current sprint; review sprint report metrics.
4. Review carryover stories and newly added items; decide what stays.
5. Pull high-priority, ready-to-work backlog items into the sprint.
6. Assign story points to unestimated items; assign owners.
7. Check total SP against capacity; adjust scope if over- or under-committed.
8. Define clear, outcome-oriented sprint goals.
9. Start the sprint.

**After the meeting:** Save completed SP totals to the sprint and release tab in the Sprint Capacity Calculator.

### Refinement (Mid-Sprint)

1. Evaluate current sprint progress using the board and sprint report; identify blockers.
2. Create the next sprint in Jira.
3. Review and adjust backlog priorities based on latest product direction.
4. Move high-priority, clearly defined items into the next sprint.
5. Assign SP and assignees to unestimated or unassigned items.
6. Assign action items for any stories requiring additional preparation.

### Retrospective

**Preparation:** Create a dedicated Miro board for the sprint using a fresh template.

**Agenda:**

1. Participants populate the board (went well, didn't, improvement ideas).
2. Each person shares their items.
3. Team votes on topics to discuss.
4. Discuss in vote-count order; timebox each topic.
5. Capture key takeaways and assign action items with owners in the meeting doc.

---

## Sprint Policies

### Sprint Capacity Target

Each team member targets **8 story points per sprint** (acceptable range: 8–10). Capacity is adjusted for PTO and holidays. Do not plan a sprint that is overcommitted or undercommitted relative to the calculated capacity.

### Sprint Churn

Churn = adding or removing a story after the sprint has started.

**Rule:** When churning an item **in**, churn an equal number of story points **out**. This maintains the sprint's SP goal and prevents scope creep.

**For bugs:** We plan sprints against the ideal case (no unexpected bugs). When a bug occurs, decide if it's important enough to displace a planned story. If yes, remove equal SP before adding the bug.

---

## Bug Triage

**Goal:** Move a bug from `NEW` to `ASSIGNED` (i.e., triaged and being worked) or determine next steps (reassign, close).

### Step 1: Check required fields

- **Severity** — should be set by reporter; estimate if missing.
- **Priority** — set by triager; reflects engineering view of importance (does not need to match severity).
- **Affects Version** — all versions where the bug is known to exist.
- **Release Blocker**:
  - LVMS bugs: always **Rejected** (LVMS does not block OCP releases).
  - SNO/TNA/TNF bugs: assess during triage; set to Proposed if potentially blocking.

**Step 2a: LVMS bugs** — require a must-gather at minimum (confirms deployment topology and LVMS CRs).

**Step 2b: SNO / TNA / TNF bugs** — require a must-gather; sosreport may be needed for OS-level issues. Verify the issue is actually topology-specific before accepting the bug.

### Step 3: Working the bug

- Set **Target Version** (e.g., `4.16.0` — use full y.z.0, not `4.16`).
- Set **Target Backport Versions** after consulting reporter and PM; minimize unnecessary backports.
- Include the bug number in the PR title: `OCPBUGS-12345: Fix description`. This triggers Jira automation to update bug status as the PR progresses.

**Churning bugs into a sprint:** Bugs of sufficient severity/priority or that are release blocking should be churned into the sprint per the Sprint Churn policy.

---

## Work Prioritization

Prioritization flows top-down: Features/Initiatives → Epics → Scrum Backlog.

**Level 1 (Features/Initiatives):** Stack-ranked by PM (Daniel Froehlich). EE provides input based on capacity, complexity, and domain knowledge. Priorities cascade to child epics.

**Level 2 (Epics):** Manager, Team Lead, and PM stack-rank epics within priority groups. Cutline epics are identified (must-complete vs. should-complete for the release).

**Level 3 (Scrum Backlog):** Stories inherit the priority of their parent epic. Diverging from the epic's priority requires strong justification — stories with a lower priority than their epic risk never being pulled into a sprint.

---

## Epic Refinement Process

**Assignee** is responsible for getting an epic from Planning → To Do.

1. **Set baseline fields:** Component, Labels, QA Contact, Doc Contact, Size.
2. **Fill out epic description** using the standard template (goal, dependencies, completion criteria).
3. **Create stories:** Either directly (if implementation is clear) or via a refinement spike to allocate sprint capacity for investigation.
4. Move epic to **To Do** when steps 1–3 are complete.

**QA Contact:** If no QE is needed, set to `unassigned_jira`. Do not leave blank.
**Doc Contact:** If no docs are needed, set to `unassigned_jira`. Do not leave blank.

---

## Feature / Initiative Refinement (SME Process)

The **SME** role is responsible for feature refinement. Assigned during release planning.

1. **Verify feature details:** Architect, SME, and Assignee are set; description has a clear goal.
2. **Create a refinement Spike** in OCPEDGE. Set component to match the feature. Spike must have a "blocks" relationship to the Feature/Initiative.
3. **Spike completion criteria:** All open questions answered, all dependencies identified, enough knowledge to write implementation stories.
4. **After spike:** Create deliverable Epics. Leave a comment on the Feature/Initiative indicating it's ready to move to "Backlog" state.

**Important:** Features should only contain epics that are **required** for the feature to complete. Optional or nice-to-have epics belong in an Initiative or as standalone epics.

---

## Key Roles

### SME

Engineering lead for a Feature/Initiative. Responsible for refinement, understanding desired outcomes, and raising questions with PM.

### Epic Assignee

Accountable for epic refinement into deliverable stories, story pointing, sprint planning, and maintaining accurate epic description.

### Scrum Master

Operational role. Leads all sprint ceremonies; ensures 100% of sprint stories are SP'd; ensures 100% of epics are sized; manages Jira dashboards, filters, and automations; unblocks Jira workflow issues.

### Team Lead

Technical role. Drives architectural alignment; advises on release backlog ranking; ensures bugs are triaged; monitors CI; responsible for at least one component lead role in OCPBUGS.

### Payload Manager (Rotational)

**Daily:** Check nightly release status for 4.18–current nightlies; check Jira tickets; monitor CI Slack channels (`#ci-single-node`, `#ci-two-node-arbiter`, `#ci-two-node-fencing`, `#forum-ocp-release-oversight`, `#announce-testplatform`); attend TRT standup; debug and file Jira tickets for CI failures.

**Weekly:** Update Payload Manager doc; check component readiness regressions via Sippy (4.18–4.21 HA vs single comparisons); sync with next rotation person.

**Sprintly:** Hand off to next rotation; update `edge-enablement-payload-manager` Slack alias.

---

## Jira Conventions for Agents

- **Issue ownership:** An issue belongs to the team if the assignee **or** QA Contact (`customfield_10470`) is a roster member.
- **Bugs always 0 SP.** Never suggest non-zero SP for a bug.
- **Epics use T-shirt sizes**, not SP. Stories/Spikes/Tasks/Bugs use SP.
- **Target version format:** Always use `4.x.0` (e.g., `4.16.0`) or `5.x.0`. Never use `4.x` or `5.x` alone.
- **LVMS bugs:** Never set Release Blocker to anything other than "Rejected".
- **Backlog entry point:** Apply `ocpedge-plan` label to Outcomes, Features, or Epics to include them in the Jira Plan.
- **OCPBUGS PR title format:** `OCPBUGS-<number>: <description>` — required to trigger status automation.
- **Epic Status field:** Does not auto-update on closure. The team has automation for this — do not manually change unless directed.
- **Automation actor:** Use "Automation for Jira" as the rule Actor (not personal accounts or bot accounts) for new automation rules.
- **Sprint SP goal:** 8 SP per person. Verify this when analyzing sprint health or recommending tickets to add.
- **Stories not linked to an epic** are non-compliant with team conventions. Flag these during grooming.
- **Telco-relevant epics** require the **Market Portfolio** field set at the epic level to appear on Telco dashboards.
