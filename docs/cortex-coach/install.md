# Install

## Prerequisites

- Python 3.10+
- `uv` (recommended)
- `just` (recommended for task shortcuts)

## Standalone Install (Recommended)

Install from the standalone repository:

```bash
uv tool install git+https://github.com/JustAHobbyDev/cortex-coach.git
```

Run:

```bash
cortex-coach --help
```

Pip fallback:

```bash
pip install git+https://github.com/JustAHobbyDev/cortex-coach.git
```

## In-Repo Script Mode (Temporary Fallback)

If you do not want to install, run directly from repo root:

```bash
python3 scripts/cortex_project_coach_v0.py --help
```

Or use `just` recipes:

```bash
just --list
```

This fallback is transitional and will be removed after full decoupling.
