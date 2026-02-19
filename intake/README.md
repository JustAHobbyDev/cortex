# Intake Policy

Purpose: stage external source material for review, then distill durable insights into Cortex canonical artifacts.

## Tracking Policy

Tracked in git:
- `intake/README.md` (this policy)
- `intake/sources.md` (source registry)
- curated synthesis notes under `intake/candidate/` when they contain distilled insights worth review

Not tracked in git:
- raw cloned repositories under `intake/books/`
- raw source dumps, generated extracts, and temporary scratch artifacts

## Workflow

1. Add external source material under `intake/books/` (local only).
2. Register each source in `intake/sources.md` with URL, commit/version, license, and retrieval date.
3. Produce concise synthesis notes in `intake/candidate/`.
4. Promote durable insights into canonical Cortex surfaces (`principles/`, `patterns/`, `contracts/`, `specs/`, `templates/`, `playbooks/`, `policies/`, `philosophy/`, `operating_model/`).
5. Keep `intake/` as a staging surface, not a long-term archive.

## Guardrails

- Do not commit full third-party repositories or large raw corpora into Cortex.
- Preserve attribution and license metadata in `intake/sources.md`.
- Prefer high-signal synthesis over verbatim copying.
