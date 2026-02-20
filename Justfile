set shell := ["bash", "-lc"]

default:
  @just --list

coach-init project_dir project_id project_name:
  uv run python3 scripts/cortex_project_coach_v0.py init \
    --project-dir "{{project_dir}}" \
    --project-id "{{project_id}}" \
    --project-name "{{project_name}}"

coach-audit project_dir:
  uv run python3 scripts/cortex_project_coach_v0.py audit \
    --project-dir "{{project_dir}}"

coach-cycle project_dir:
  uv run python3 scripts/cortex_project_coach_v0.py coach \
    --project-dir "{{project_dir}}"

coach-cycle-apply project_dir apply_scope="direction,governance,design":
  uv run python3 scripts/cortex_project_coach_v0.py coach \
    --project-dir "{{project_dir}}" \
    --apply \
    --apply-scope "{{apply_scope}}"

design-dsl-compile dsl_file out_file:
  uv run python3 scripts/design_prompt_dsl_compile_v0.py \
    --dsl-file "{{dsl_file}}" \
    --out-file "{{out_file}}"

design-validate:
  uv run python3 scripts/design_ontology_validate_v0.py
