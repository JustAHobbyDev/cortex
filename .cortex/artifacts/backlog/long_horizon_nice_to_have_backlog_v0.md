# Long-Horizon Nice-to-Have Backlog v0

- Date: 2026-02-25
- Scope: Non-blocking improvements that strengthen portability, governance durability, and operator experience over time.
- Classification: Nice-to-have only (not required for current phase completion).

## Tier Definitions

1. `P3`: High-value enhancements worth planning when capacity allows.
2. `P4`: Exploratory/optional enhancements with longer payoff horizons.

## Backlog Items

| ID | Item | Tier | Suggested Owner Role | Value | Non-Blocking Exit Signal |
|---|---|---|---|---|---|
| NTH-001 | Expand portability matrix to `>=8` stack shapes | P3 | Program Lead + Delivery Operations Lead | Strengthens portability claims beyond two archetypes | Harness supports 8+ shapes with pass/fail summary artifact |
| NTH-002 | Add ecosystem coverage for Go/Rust/Java/.NET | P3 | Delivery Operations Lead | Improves cross-language adoption readiness | At least one passing pilot per added ecosystem |
| NTH-003 | Add CI provider matrix (GitHub/GitLab/local parity) | P3 | CI/Gate Owner | Reduces provider-specific blind spots | Published parity report across providers |
| NTH-004 | Add OS matrix (Linux/macOS/Windows) | P3 | Runtime Reliability Lead | Hardens portability across runner environments | Multi-OS run artifact with no policy regressions |
| NTH-005 | Stack-shape auto-detection with profile recommendations | P3 | Runtime Reliability Lead | Lowers operator setup friction | Deterministic profile recommendation output in bootstrap report |
| NTH-006 | Optional stack template packs | P3 | Delivery Operations Lead | Faster onboarding for common archetypes | Template pack registry + usage docs |
| NTH-007 | Scheduled drift canary runs for portability matrix | P3 | CI/Gate Owner | Detects long-term regressions early | Recurring canary artifact with trend history |
| NTH-008 | Governance observability dashboard | P3 | Program Lead | Better decision support for reliability/overhead trends | Dashboard source artifact generated from existing reports |
| NTH-009 | Policy simulation mode (`what-if`) | P4 | Governance Policy Lead | Safer policy evolution before rollout | Simulation report with predicted failures and blast radius |
| NTH-010 | Multi-agent role simulation harness | P4 | Governance Enforcement Lead | Validates escalation and handoff behavior under stress | Harness report covering role conflict/escalation scenarios |
| NTH-011 | Incremental/cached gate execution | P3 | CI/Gate Owner | Reduces CI runtime/cost while preserving rigor | Measured CI runtime reduction with no false-pass increase |
| NTH-012 | Large-repo and low-resource stress suites | P3 | Runtime Reliability Lead | Improves confidence in constrained environments | Stress test report with SLO/timeout outcomes |
| NTH-013 | Mature-repo migration assistant | P3 | Delivery Operations Lead | Eases adoption in existing production repos | Migration checklist + assistant output artifact |
| NTH-014 | Signed governance attestations | P4 | Governance Enforcement Lead | Tamper-evident closeout chain | Signature verification artifact linked to closeout reports |
| NTH-015 | Policy/schema migration tooling | P3 | Contract/Schema Lead | Reduces upgrade risk and manual drift | Versioned migration commands + rollback notes |
| NTH-016 | Role-based onboarding lab tracks | P4 | Program Lead + Delivery Operations Lead | Improves onboarding effectiveness | Lab completion artifact mapped to role capabilities |
| NTH-017 | Adapter/plugin SDK for custom gates | P4 | Runtime Reliability Lead | Enables extension without core edits | SDK contract + sample plugin passing contract checks |
| NTH-018 | Portfolio-level multi-repo reporting | P4 | Program Lead | Improves executive-level governance visibility | Aggregated portfolio report artifact across repos |

## Suggested Planning Order (When Capacity Opens)

1. `NTH-001` expand matrix stack shapes.
2. `NTH-011` incremental/cached gate execution.
3. `NTH-003` CI provider parity matrix.
4. `NTH-012` stress suites for large/low-resource repos.

## Notes

1. This backlog is intentionally non-blocking and should not alter release-boundary gate requirements unless a promoted decision explicitly changes policy.
2. Items can be promoted into phase-scoped ticket boards when owner, metrics, and budget are explicitly assigned.
