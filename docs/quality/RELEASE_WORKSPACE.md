# Release Workspace Cleanup - 27.0.0-safe

Python validation commands create generated files such as `__pycache__` and `.pyc` files. These files are harmless locally but should not be committed or shipped in the portfolio ZIP.

`27.0.0-safe` adds:

```bash
python scripts/clean_release_artifacts.py
```

The cleanup removes reproducible generated artifacts:

- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- `*.pyc`
- `*.pyo`
- `*.log`
- simulator `logs/` and `data/` folders

It deliberately avoids `.venv` deletion so a local development environment is not accidentally destroyed. The build script excludes virtual environments from the output ZIP.

Use dry-run mode before deleting:

```bash
python scripts/clean_release_artifacts.py --dry-run
```
