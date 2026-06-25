# To Do

## TODO002: ruff configuration

- Some basic stuff (unused return values etc.) not being detected

## TODO007: Command to create symlinks or `.cmd` wrappers for all scripts

## TODO009: We should respect the pinned Python version during `init`

e.g. `.pydl.json`, `.python-version` etc.

## Done

### ~~TODO000: Generalization~~ (fixed)

- `fmt_cmd.py`: Hardcodes ruff as the linting tool
- `lint_cmd.py`: Hardcodes ruff as the linting tool

### ~~TODO001: Recode~~ (fixed)

- Introduce `--fix/--check`
- What should the default be?
- What should return codes be?
- Add to `check`

### ~~TODO003: Reduce number of warnings in output~~ (fixed)

### ~~TODO004: Include `vulture` to detect dead code and unused return values~~ (implemented)

### ~~TODO005: `init` should indicate which Python it's using~~ (no repro)

### ~~TODO006: Simple project (e.g. `wav-tool`) `init does not do pip install?~~ (fixed)

### ~~TODO008: Command to create `pre-commit` hooks file~~ (fixed)
