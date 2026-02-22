# Quickstart

Assumption: `cortex-coach` is installed and on your `PATH`.

## Minimal Workflow (Recommended First Run)

Use this path to get first success quickly with minimal ceremony.

### 1) Install

```bash
uv tool install \
  git+https://github.com/JustAHobbyDev/cortex-coach.git@main
```

### 2) Initialize

```bash
cd /path/to/your/project
```

```bash
cortex-coach \
  init \
  --project-dir . \
  --project-id my_project \
  --project-name "My Project"
```

### 3) Risk Check

```bash
cortex-coach \
  audit-needed \
  --project-dir . \
  --format json
```

If `audit_required=true`, run:

```bash
cortex-coach \
  coach \
  --project-dir .
```

```bash
cortex-coach \
  audit \
  --project-dir .
```

### 4) Pre-Merge Gate

```bash
./scripts/quality_gate_v0.sh
```

## External Project Example (Copy/Paste)

```bash
mkdir -p ~/projects/acme-admin
cd ~/projects/acme-admin
cortex-coach init \
  --project-dir . \
  --project-id acme_admin \
  --project-name "Acme Admin Dashboard"
cortex-coach coach --project-dir .
cortex-coach audit --project-dir .
```

## 1) Initialize a Project

```bash
cortex-coach init \
  --project-dir /path/to/project \
  --project-id my_project \
  --project-name "My Project"
```

Equivalent `just` recipe:

```bash
just coach-init /path/to/project my_project "My Project"
```

## 2) Run a Coach Cycle

```bash
cortex-coach coach \
  --project-dir /path/to/project
```

Equivalent:

```bash
just coach-cycle /path/to/project
```

## 3) Run an Audit

```bash
cortex-coach audit \
  --project-dir /path/to/project
```

Equivalent:

```bash
just coach-audit /path/to/project
```

## 4) Optional: Apply Drafts

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --apply \
  --apply-scope direction,governance
```

## Complete Workflow (Governance + Reflection)

Use this when running full governance discipline, not just minimal onboarding.

### 1) Install cortex-coach

```bash
uv tool install \
  git+https://github.com/JustAHobbyDev/cortex-coach.git@main
```

### 2) Initialize your project

```bash
cd /path/to/your/project
```

```bash
cortex-coach \
  init \
  --project-dir . \
  --project-id my_project \
  --project-name "My Project"
```

### 3) Start work with a quick risk check

```bash
cortex-coach \
  audit-needed \
  --project-dir . \
  --format json
```

If `audit_required=true`, run:

```bash
cortex-coach \
  coach \
  --project-dir .
```

```bash
cortex-coach \
  audit \
  --project-dir .
```

### 4) Make changes normally (code/docs/policies/etc.)

### 5) Capture governance decisions when they happen

```bash
cortex-coach \
  decision-capture \
  --project-dir . \
  --title "..." \
  --decision "..." \
  --rationale "..." \
  --impact-scope governance,docs \
  --linked-artifacts path1,path2
```

```bash
cortex-coach \
  decision-promote \
  --project-dir . \
  --decision-id <decision_id>
```

### 6) When a mistake repeats, run reflection loop

```bash
cortex-coach \
  reflection-scaffold \
  --project-dir . \
  --title "..." \
  --mistake "..." \
  --pattern "..." \
  --rule "..." \
  --format json
```

Use scaffold output to run `decision-capture` with `--reflection-id` and `--reflection-report`.

### 7) Run completeness checks before merge

```bash
cortex-coach \
  decision-gap-check \
  --project-dir . \
  --format json
```

```bash
cortex-coach \
  reflection-completeness-check \
  --project-dir . \
  --required-decision-status candidate \
  --format json
```

```bash
python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json
```

```bash
python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json
```

```bash
cortex-coach \
  audit \
  --project-dir . \
  --audit-scope cortex-only
```

Optional full-scope:

```bash
cortex-coach \
  audit \
  --project-dir . \
  --audit-scope all
```

### 8) Run quality gate

```bash
./scripts/quality_gate_v0.sh
```

CI uses:

```bash
./scripts/quality_gate_ci_v0.sh
```

### 9) Merge/release only when gates are green

- No uncovered decision gaps
- Reflection completeness passes
- Audit passes
- Tests pass

## If `cortex-coach` Is Not Installed (Temporary Migration Fallback)

Use:

```bash
python3 scripts/cortex_project_coach_v0.py <command> ...
```

Prefer installing standalone `cortex-coach`; script fallback is transitional during decoupling.

## Expected Output Location

Inside the target project:

- `.cortex/manifest_v0.json`
- `.cortex/artifacts/*`
- `.cortex/prompts/*`
- `.cortex/reports/*`
