# Gate Registry

`27.0.0-safe` adds a central registry for reviewer-facing quality gates.
The goal is simple: the package now has many checks, so reviewers should be
able to verify which script, document, and optional API endpoint belongs to each
quality gate without chasing scattered README sections.

Run:

```bash
python scripts/check_gate_registry.py
```

or inspect:

```bash
curl http://127.0.0.1:5000/api/gates
```

This gate checks that:

- quality-gate scripts exist;
- quality-gate documentation exists;
- reviewer-facing gate endpoints are declared in `project_manifest.json`;
- gate endpoints are documented in OpenAPI and the API reference;
- `project_manifest.json` still declares the safe simulator boundary.

## What this does not prove

This is a release-maintenance check only. It does **not** prove live IPv6 traffic
monitoring, packet capture, packet sending, active network scanning, intrusion
detection accuracy, or production readiness.
