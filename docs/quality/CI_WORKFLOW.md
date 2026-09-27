# CI Workflow Sanity Gate - 27.0.0-safe

Run the lightweight workflow contract check with:

```bash
python scripts/check_ci_workflow.py
```

The repository intentionally avoids adding a YAML parser dependency only for source-package validation. The checker therefore performs bounded text-based checks for the workflow requirements that matter to the handoff.

It verifies:

- current `actions/checkout@v7` and `actions/setup-python@v7` actions are present
- required validation commands remain in `.github/workflows/ci.yml`
- the Ubuntu Python 3.10/3.11/3.12 validation matrix remains present
- a `windows-latest` Python 3.12 validation job remains present
- the Windows job runs clean validation, full unittest discovery, release ZIP hygiene, and the workflow contract check
- multi-command shell steps use `run: |` instead of malformed single-line YAML

The check is not a replacement for GitHub Actions execution. Its purpose is to fail locally when the committed workflow drifts away from the documented Linux/Windows validation contract.
