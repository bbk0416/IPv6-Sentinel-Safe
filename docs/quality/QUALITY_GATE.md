# Quality Gate

This project is judged as a **local-only IPv6 security monitoring simulator**, not as a production IDS/NDR product.

The current quality gate checks four things:

1. The safe release ID matches across settings, OpenAPI, manifest, and handoff docs, while `pyproject.toml` uses the normalized PEP 440 package version.
2. Required review documents exist.
3. Release packages do not include runtime artifacts such as `.venv`, `logs`, `backup`, or `__pycache__`.
4. The codebase remains simulation-only, with no Scapy/mitmproxy/WMI runtime imports and no real packet capture/send/scan flags.

Run it locally:

```bash
python scripts/release_audit.py
```

Or through the dashboard API:

```bash
curl http://127.0.0.1:5000/api/quality
```

A `pass` result means the project is suitable for portfolio/demo review. It does **not** mean the project is a real network monitoring product.

## Requirements check

This release includes `scripts/check_requirements.py`. It is not a package installer. It checks the declared dependency manifest for required local-web-app packages and blocks reintroduction of packet capture/injection/interception libraries.

## Release artifact input

The quality gate now includes the release artifact hygiene check from `services/release_artifact.py`. This verifies that the source tree is suitable for handoff by excluding runtime/cache artifacts and including required release files. It is still a packaging check, not a real network detection test.

## Local reviewer workspace note

Reviewers may create `.venv/` in the project root as shown in the README. Source-tree quality gates ignore that local tooling folder, while release ZIP validation and `scripts/build_release.py` still keep virtualenv contents out of handoff archives.

