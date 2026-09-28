# CI Workflow Sanity Gate - 27.0.0-safe

Run the lightweight workflow contract check with:

```bash
python scripts/check_ci_workflow.py
```

The repository intentionally avoids adding a YAML parser dependency only for source-package validation. The checker therefore performs bounded text-based checks for the workflow requirements that matter to the handoff.

It verifies:

- GitHub Actions are pinned to full commit SHAs instead of mutable major-version tags
- the workflow declares least-privilege `permissions: contents: read`
- checkout steps use `persist-credentials: false`
- required validation commands remain in `.github/workflows/ci.yml`
- the Ubuntu Python 3.10/3.11/3.12 validation matrix remains present
- a `windows-latest` Python 3.12 validation job remains present
- the Windows job runs clean validation, full unittest discovery, release ZIP hygiene, and the workflow contract check
- multi-command shell steps use `run: |` instead of malformed single-line YAML

Current pinned actions:

- `actions/checkout` v7 tag target: `3d3c42e5aac5ba805825da76410c181273ba90b1`
- `actions/setup-python` v7 tag target: `5fda3b95a4ea91299a34e894583c3862153e4b97`

The check is not a replacement for GitHub Actions execution. Its purpose is to fail locally when the committed workflow drifts away from the documented Linux/Windows validation and CI security contract.
