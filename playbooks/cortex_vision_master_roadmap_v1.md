# Cortex Vision Master Roadmap v1

## Purpose

Define the remaining end-to-end path from current state to a friction-reduced, project-agnostic governance operating layer.

## Current Baseline

- `cortex`: governance/source-of-truth artifacts are active and enforced.
- `cortex-coach`: standalone runtime exists with decision and reflection enforcement.
- CI/local gates are functional but still repo-specific in shape.

## Vision Target

`cortex + cortex-coach` should provide:

1. Fast onboarding (first-success in minutes)
2. Strong governance integrity (decision + reflection + audit traceability)
3. Project-agnostic portability (framework core + project adapters)
4. Low operational overhead (minimal command burden)
5. Durable learning across sessions and agents

## Guiding Constraints

- Governance enforcement must remain artifact-based, not chat-memory-based.
- Runtime behavior belongs in `cortex-coach`; governance model belongs in `cortex`.
- Project-specific checks must be configurable adapters, not hardcoded assumptions.

## Roadmap Phases

### Phase 1: Workflow Compression

Goal: reduce operator command complexity.

Deliverables:
- Add single-entry flow command in coach (for example `cortex-coach flow`).
- Support `--mode minimal|full` to route minimal vs full governance workflow.
- Ensure flow emits deterministic reports under `.cortex/reports/`.

Exit Criteria:
- New user can reach first green quality gate with one primary command path.
- Existing checks still enforce decision/reflection/audit integrity.

### Phase 2: Project-Agnostic Gate Framework

Goal: replace one-off gate scripts with portable framework + adapters.

Deliverables:
- Define gate core contract:
  - governance checks (required)
  - adapter checks (configurable)
- Add adapter model (examples):
  - `python-pytest`
  - `node-test`
  - `cargo-test`
  - `custom-command`
- Add scaffold command to generate project gate config and scripts.

Exit Criteria:
- New projects can bootstrap gates without manual script authoring.
- Repo-specific assumptions are moved behind adapter config.

### Phase 3: Agent-Oriented Operating Defaults

Goal: improve automatic governance conformance in AI-assisted workflows.

Deliverables:
- Standardized agent prompt/runbook snippets for minimal and full modes.
- Reflection trigger policy template (repeat-mistake and gate-failure scenarios).
- Hand-off bundle standard for agent context loading in active tasks.

Exit Criteria:
- Agents consistently invoke governance flow without manual reminder loops.
- Reflection-to-decision closure rates trend upward.

### Phase 4: Governance Completeness Hardening

Goal: tighten enforcement from “good practice” to “reliable guarantees.”

Deliverables:
- Optional stricter mode:
  - require promoted decisions for reflection closure in CI (`promoted` mode)
- Add completeness dashboard report:
  - reflections created
  - reflections mapped to decisions
  - uncovered governance-impact changes
- Add policy for escalation when completeness drops below threshold.

Exit Criteria:
- Completeness checks are measurable and auditable over time.
- Governance regression is detectable within one CI cycle.

### Phase 5: Adoption + Migration Program

Goal: make rollout repeatable across projects.

Deliverables:
- Migration guide: legacy scripts -> adapter-based framework.
- Templates for greenfield project onboarding.
- Reference implementations for at least 3 different stacks.

Exit Criteria:
- At least 3 heterogeneous projects onboarded with passing gates.
- Time-to-first-green reduced versus current baseline.

## Milestones and Sequencing

1. Phase 1 (workflow compression) before broad adoption push.
2. Phase 2 (adapter framework) before claiming project-agnostic portability.
3. Phase 3 and 4 can run in parallel once Phase 2 baseline lands.
4. Phase 5 starts after Phase 2 minimum viability.

## Success Metrics

- Onboarding:
  - median time from install to first green gate
- Reliability:
  - rate of governance-impact changes with decision coverage
- Reflection quality:
  - reflection scaffold -> decision mapping rate
- Portability:
  - number of projects/stacks running adapter-based gates
- Operator overhead:
  - median commands executed per feature/change closeout

## Risks and Mitigations

- Risk: framework over-design slows delivery.
  - Mitigation: ship adapter model with 2-3 concrete adapters first.
- Risk: strict governance creates contributor friction.
  - Mitigation: minimal mode + progressive hardening.
- Risk: drift between `cortex` contract and `cortex-coach` runtime.
  - Mitigation: contract tests and paired change discipline.

## Immediate Next Actions

1. Implement Phase 1 flow command design proposal.
2. Draft Phase 2 adapter contract spec in `cortex`.
3. Add a tracking board section in playbooks for phase-level progress and dates.
