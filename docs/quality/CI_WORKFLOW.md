# CI Workflow Sanity Gate - 27.0.0-safe

`27.0.0-safe` adds a lightweight CI workflow sanity check:

```bash
python scripts/check_ci_workflow.py
```

This project avoids adding a YAML parser dependency just for source-package validation, so the check is intentionally simple. It verifies that the GitHub Actions workflow contains the required validation commands and catches a common YAML mistake: placing multiple shell commands under a single-line `run:` step without using `run: |`.

The check is not a replacement for running GitHub Actions on GitHub. It is a local guard against obvious workflow drift before publishing the repository.
