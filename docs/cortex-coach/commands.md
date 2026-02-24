# Commands

Examples below use installed CLI form (`cortex-coach`).
Fallback (temporary migration path): `python3 scripts/cortex_project_coach_v0.py ...`

In this repository, `just coach-*` recipes now route through
`scripts/cortex_coach_wrapper_v0.sh` (Phase 3 dual-path stabilization):
- prefer installed `cortex-coach`
- fallback to in-repo script mode
- set `CORTEX_COACH_FORCE_INTERNAL=1` to force script mode for parity checks
- script fallback is temporary and will be removed in full decoupling

Common option:
- `--assets-dir /path/to/cortex-assets` to load contract/schema/vocabulary assets from an external Cortex asset root.

Output format contract:
- Non-interactive commands should be runnable in both text and JSON modes (`--format text|json`).
- Until standalone runtime parity is complete for every command, use the delegator entrypoint for universal JSON support:
  - `python3 scripts/cortex_project_coach_v0.py <command> ... --format json`
- Native standalone JSON support exists for a subset of commands (`audit-needed`, `context-policy`, decision/reflection commands, `contract-check`).

## Phase 1 Tactical Memory Commands (Design Baseline)

The following command family is a Phase 1 design contract baseline and is not fully implemented yet:

| Command | Intended Role | Status |
|---|---|---|
| `memory-record` | capture tactical memory records | design baseline |
| `memory-search` | retrieve ranked tactical records | design baseline |
| `memory-prime` | produce bounded priming bundles | design baseline |
| `memory-diff` | compare tactical record sets/snapshots | design baseline |
| `memory-prune` | remove stale/non-compliant tactical records | design baseline |
| `memory-promote` | bridge tactical evidence to canonical promotion flow | design baseline |

Shared command-family expectations:
- `--project-dir` is required.
- `--format text|json` must be supported for non-interactive usage.
- Omitting `--format` defaults to text output for backward compatibility.
- Mutation-class commands (`memory-record`, `memory-prune`, `memory-promote`) must expose lock controls:
  - `--lock-timeout-seconds`
  - `--lock-stale-seconds`
  - `--force-unlock`

Baseline exit code contract:
- `0`: success
- `2`: invalid arguments/contract shape violation
- `3`: policy violation
- `4`: lock/state conflict
- `5`: internal runtime failure

Canonical source:
- `contracts/tactical_memory_command_family_contract_v0.md`

### `memory-promote` Bridge Mapping (PH1-006 Design Baseline)

`memory-promote` is the tactical-to-governance bridge and must map output fields into
`contracts/promotion_contract_schema_v0.json`:

| `memory-promote` output | Promotion contract field |
|---|---|
| decision/reflection ids | `decision_reflection_linkage` |
| impacted artifact summaries | `impacted_artifacts` |
| rationale + evidence refs | `rationale_evidence_summary` |
| source lineage + trace metadata | `promotion_trace_metadata` |

Bridge expectations:
- Governance-impacting promotion attempts fail closed if any required promotion contract section is missing.
- Bridge trace metadata should set `bridge_command=memory-promote`.
- Non-governance outputs must be explicitly marked so they are not interpreted as canonical governance closure.

## `init`

Bootstrap `.cortex/` artifacts in a target project.

```bash
cortex-coach init \
  --project-dir /path/to/project \
  --project-id my_project \
  --project-name "My Project" \
  --cortex-root .cortex \
  --assets-dir /path/to/cortex-assets
```

Key options:

- `--force`: overwrite existing bootstrap artifacts
- `--lock-timeout-seconds <n>`
- `--lock-stale-seconds <n>`
- `--force-unlock`

## `audit`

Validate lifecycle artifacts and emit a health report.

```bash
cortex-coach audit \
  --project-dir /path/to/project \
  --cortex-root .cortex \
  --audit-scope cortex-only \
  --assets-dir /path/to/cortex-assets
```

`--audit-scope` options:
- `cortex-only` (default): conformance scans only inside the selected cortex root.
- `all`: conformance scans broader governance/spec dirs in the repository.

Output:

- `.cortex/reports/lifecycle_audit_v0.json`
- includes `spec_coverage` findings when `.cortex/spec_registry_v0.json` exists
- includes `artifact_conformance` findings (for example foreign project scope references)

JSON output (delegator compatibility path):

```bash
python3 scripts/cortex_project_coach_v0.py audit \
  --project-dir /path/to/project \
  --audit-scope all \
  --format json
```

Spec coverage registry is bootstrapped by `init` at:
- `.cortex/spec_registry_v0.json`

### `.cortexignore` exclusions

`audit` and conformance checks support project-local exclusions via `.cortexignore`
using gitignore-style glob patterns.

Example:

```text
# ignore imported reference docs
philosophy/legacy_imports/**

# keep one file included
!philosophy/legacy_imports/README.md
```

## `audit-needed`

Determine whether an audit should run now based on dirty-file risk tiers.

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project
```

JSON mode + CI-friendly fail behavior:

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project \
  --format json \
  --fail-on-required
```

Optional report output:

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project \
  --out-file .cortex/reports/audit_needed_v0.json
```

## `contract-check`

Validate the target project against the coach asset contract.

```bash
cortex-coach contract-check \
  --project-dir /path/to/project \
  --assets-dir /path/to/cortex-assets
```

JSON output:

```bash
cortex-coach contract-check \
  --project-dir /path/to/project \
  --format json
```

Use a custom contract file:

```bash
cortex-coach contract-check \
  --project-dir /path/to/project \
  --contract-file /path/to/coach_asset_contract_v0.json
```

## `coach`

Run one lifecycle guidance cycle.

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --cortex-root .cortex \
  --audit-scope cortex-only
```

Outputs:

- `.cortex/reports/coach_cycle_<timestamp>_v0.json`
- `.cortex/reports/coach_cycle_<timestamp>_v0.md`
- `.cortex/prompts/coach_cycle_prompt_<timestamp>_v0.md`

### `coach --apply`

Generate draft `vN+1` artifact files for eligible actions.

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --apply
```

### `coach --apply-scope`

Limit draft generation to:

- `direction`
- `governance`
- `design`

Example:

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --apply \
  --apply-scope direction,design
```

## `context-load`

Generate a bounded context bundle for agent handoff.

```bash
cortex-coach context-load \
  --project-dir /path/to/project \
  --task "design drift" \
  --max-files 10 \
  --max-chars-per-file 2000 \
  --fallback-mode priority \
  --assets-dir /path/to/cortex-assets
```

Optional file output:

```bash
cortex-coach context-load \
  --project-dir /path/to/project \
  --task "governance updates" \
  --out-file .cortex/reports/agent_context_bundle_v0.json
```

JSON mode with explicit format flag (delegator compatibility path):

```bash
python3 scripts/cortex_project_coach_v0.py context-load \
  --project-dir /path/to/project \
  --task "governance updates" \
  --format json
```

`--fallback-mode priority` enables a fallback chain:
1. restricted budget
2. relaxed budget
3. unrestricted (no file/char limits) if prior levels fail

Phase 2 contract baseline (`PH2-001`, implementation target):
- Canonical contract source: `contracts/context_load_retrieval_contract_v0.md`
- Ranked retrieval order is deterministic and includes explicit tie-break rules.
- Weighting mode and retrieval profile are contract-bounded and default to backward-compatible deterministic behavior.
- JSON output should carry score breakdown, provenance, and confidence metadata for selected entries.
- Gate C evaluation uses frozen fixture/query set: `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`

## `context-policy`

Analyze repository shape and recommend task focus + context budgets.

```bash
cortex-coach context-policy \
  --project-dir /path/to/project \
  --format json \
  --out-file .cortex/reports/context_policy_v0.json
```

## `policy-enable`

Enable an opt-in policy file inside the target project.

```bash
cortex-coach policy-enable \
  --project-dir /path/to/project \
  --policy usage-decision
```

Default output path:
- `.cortex/policies/cortex_coach_usage_decision_policy_v0.md`

Also supported:

```bash
cortex-coach policy-enable \
  --project-dir /path/to/project \
  --policy decision-reflection
```

Default output path:
- `.cortex/policies/cortex_coach_decision_reflection_policy_v0.md`

Optional overwrite:

```bash
cortex-coach policy-enable \
  --project-dir /path/to/project \
  --policy usage-decision \
  --force
```

JSON output (delegator compatibility path):

```bash
python3 scripts/cortex_project_coach_v0.py policy-enable \
  --project-dir /path/to/project \
  --policy usage-decision \
  --format json
```

## `decision-capture`

Capture a decision candidate during active work.

```bash
cortex-coach decision-capture \
  --project-dir /path/to/project \
  --title "Split local and CI quality gates" \
  --decision "Use strict local gate and CI correctness gate." \
  --rationale "Avoid dirty-tree false negatives in CI." \
  --impact-scope governance,ci,docs \
  --linked-artifacts .github/workflows/cortex-validation.yml,docs/cortex-coach/quality-gate.md
```

Writes/updates:
- `.cortex/reports/decision_candidates_v0.json`

## `reflection-scaffold`

Scaffold reflection outcomes into decision-ready metadata and follow-up commands.

```bash
cortex-coach reflection-scaffold \
  --project-dir /path/to/project \
  --title "Require reflection for repeated governance misses" \
  --mistake "Forgot to promote governance decision before closeout." \
  --pattern "Reflection was ad hoc and not encoded." \
  --rule "Run reflection scaffold before closeout when governance files are touched." \
  --format json
```

Useful options:
- `--linked-artifacts a,b,c`: explicitly include artifact paths
- `--no-auto-link-governance-dirty`: disable automatic inclusion of governance-impacting dirty files
- `--strict-generated`: include generated audit deltas when auto-linking dirty files
- `--out-file <path>`: persist scaffold report

Outputs include:
- suggested decision statement/rationale
- suggested decision artifact path
- suggested linked artifacts (explicit + auto-linked governance dirty files)
- validation checklist and recommended follow-up commands

## `decision-list`

List decision candidates or promoted decisions.

```bash
cortex-coach decision-list \
  --project-dir /path/to/project \
  --format json
```

Optional status filter:

```bash
cortex-coach decision-list \
  --project-dir /path/to/project \
  --status promoted
```

## `decision-promote`

Promote a captured decision into canonical decision artifact.

```bash
cortex-coach decision-promote \
  --project-dir /path/to/project \
  --decision-id dec_20260220T000000Z_example
```

Writes:
- `.cortex/artifacts/decisions/decision_<slug>_vN.md`
- updates `.cortex/reports/decision_candidates_v0.json`

Audit behavior:
- `audit` fails `unsynced_decisions` when promoted decisions have `impact_scope` but no `linked_artifacts`.

## `reflection_enforcement_gate_v0.py`

Fail-closed reflection enforcement used by local and CI quality gates.

```bash
python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir /path/to/project \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json
```

Checks include:
- `decision-gap-check` must pass
- `reflection-completeness-check` must pass
- matched governance-impact decisions must include valid `reflection_id` and `reflection_report`
- reflection coverage must be non-vacuous (configured minimum scaffold reports/mappings)

## `project_state_boundary_gate_v0.py`

Fail-closed boundary enforcement to keep project-instance state under `.cortex/`.

```bash
python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir /path/to/project \
  --format json
```

Checks include:
- forbidden outside-boundary roots from `contracts/project_state_boundary_contract_v0.json`
- waiver controls from `.cortex/policies/project_state_boundary_waivers_v0.json`
- expired active waivers are blocking

Notes:
- boundary root comes from `project_state_root` in the contract
- default boundary root is `.cortex/` unless contract-governed override is applied

## `just quality-gate`

Run the unified maintainer quality gate for local/CI parity.

```bash
just quality-gate
```

Fallback:

```bash
./scripts/quality_gate_v0.sh
```

## `just quality-gate-ci`

Run CI-focused correctness checks without local dirty-tree enforcement.

```bash
just quality-gate-ci
```

Fallback:

```bash
./scripts/quality_gate_ci_v0.sh
```
