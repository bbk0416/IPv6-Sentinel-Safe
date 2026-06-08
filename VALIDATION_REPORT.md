# Validation Report - 27.0.0-safe

## Scope

This report covers the safe local IPv6 security-event simulator package. It validates source/package consistency, documentation alignment, release hygiene, and simulator safety boundaries. It does **not** validate real IPv6 traffic detection, packet capture, packet sending, active network scanning, or production monitoring accuracy.

## Recommended validation command

```bash
python scripts/run_clean_validation.py
```

## v27 validation focus

`27.0.0-safe` adds the gate registry check:

```bash
python scripts/check_gate_registry.py
```

The registry verifies that reviewer-facing quality gates have matching scripts, documentation, manifest entries, and optional API endpoints.

## Expected source-package result

```txt
[OK] project validation passed
```

Runtime Flask route tests require installing `requirements.txt`. In a source-only review environment, those tests may be skipped by design.

## Honest result

- Portfolio / education simulator package: strong.
- Actual IPv6 security product: not proven and not claimed.

## v27 hotfix validation note

A runtime-dependency validation pass was added after installing `requirements.txt` in an isolated virtual environment. This found and fixed a practical quality-gate issue: starting the Flask app creates reproducible `data/`, `logs/`, and Python cache artifacts, which previously caused `/api/quality` and `scripts/check_release_artifact.py` to fail after runtime tests had executed.

The hotfix keeps those generated files out of the release ZIP, but treats already-created runtime/cache files as non-blocking validation warnings so the running app can still report the simulator's quality status correctly.

Verified checks after the hotfix:

```txt
python scripts/run_clean_validation.py
Ran 113 tests
OK

python scripts/run_clean_validation.py
status: pass

python app.py
GET /api/ready   -> 200 ready
GET /api/quality -> 200 pass
```

This still does **not** add packet capture, packet sending, real network scanning, DHCPv6/DNS spoofing, MITM, IDS, or IPS functionality.

## Final polish note

A final publication-hygiene polish was applied after the hotfix. The publication scanner now uses generic placeholder markers instead of embedding an author's private handle or email-domain markers inside the source package itself.

Final local verification with runtime dependencies installed:

```txt
python scripts/run_clean_validation.py
Ran 113 tests
OK

python scripts/run_clean_validation.py
status: pass

python scripts/final_handoff_check.py
status: pass

python scripts/check_release_zip.py <release.zip>
status: pass
```

The release remains a local safe simulator only. The package still does not provide live IPv6 packet capture, packet sending, real network scanning, exploitation, IDS, IPS, MITM, or production monitoring coverage.

## Final locked handoff note

A final handoff polish was applied after `FINAL_POLISHED` to improve runtime/test hygiene:

- `IPv6SentinelApp.shutdown()` now joins simulator/UI worker threads briefly during teardown.
- Runtime tests that construct Flask app instances now explicitly call `shutdown()`.
- `scripts/run_clean_validation.py` flushes output and uses a hard process exit after reporting so constrained review sandboxes do not hang on non-critical inherited handles.
- `docs/release/FILE_INVENTORY.json` was regenerated after the source changes.

Verified in this handoff pass:

```txt
python scripts/check_release_zip.py
status: pass
errors: []
warnings: []

python -m unittest tests.test_app_runtime tests.test_v14_schema_contract tests.test_v16_release_artifact tests.test_v19_file_inventory -v
Ran 27 tests
OK
```

As before, this validates the safe local simulator package and reviewer handoff only. It still does not validate or provide live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring coverage.

## v27 Final Audited Test-Hygiene Pass - 2026-06-02

Additional reviewer-readiness pass after `FINAL_LOCKED`:

- Renamed duplicate unittest class names in `tests/test_packaging.py` so no test class is silently overwritten during discovery.
- Moved misplaced `unittest.main()` guard in `tests/test_static_safety.py` to the end of the file so direct script execution sees every class definition.
- Added static safety checks that fail if future test modules contain duplicate top-level test class names or an early `__main__` guard.
- Re-ran focused packaging/static test groups and release hygiene checks after the patch.

This pass does not add live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring functionality. The package remains a local safe simulator.

### Additional final audit correction

A second test-discovery audit found one module (`tests/test_v27_reviewer_handoff.py`) using pytest-style top-level functions. Because the documented validation path uses `unittest`, those functions were converted into a `unittest.TestCase`. A regression check was added so future modules cannot hide tests behind module-level test functions when using unittest discovery.

## v27 final audited privacy pass

Additional reviewer-handoff hygiene was applied after the audited ZIP check:

- Runtime configuration logging now masks local IPv4, IPv6, and MAC address values before writing to console/file logs.
- A static safety test now checks that the configuration logger keeps those local identifiers masked.
- This is a privacy/portfolio hygiene improvement only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final privacy locked addendum

- Added optional quiet logging controls for constrained review/test sessions.
- Runtime tests now disable console/file logging before importing the app, preventing local `logs/` creation during normal test discovery.
- Fixed a stray Flask test-client positional argument in the settings test.
- This remains a local safe simulator only and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final test harness lock addendum

- Gate registry unit tests now call the local checker entrypoint directly instead of spawning a subprocess, avoiding constrained-sandbox hangs during full `unittest discover`.
- This is test harness hygiene only; it does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final capability test harness addendum

- Capability-boundary unit tests now call the local checker entrypoint directly instead of spawning a subprocess, avoiding constrained-sandbox hangs during full `unittest discover`.
- This is test harness hygiene only; it does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final simulation-vocabulary lock addendum

A final UI/API vocabulary pass was applied after `FINAL_PRIVACY_LOCKED`:

- The live `inventory_progress` payload now reports sample-generation count as `processed` instead of `scanned`.
- The dashboard no longer keeps the legacy `progress.scanned` fallback; current output uses `processed` only.
- The decorative CSS animation was renamed from `scan` to `safeSweep` to avoid misleading active-UI terminology.
- A static regression test now blocks reintroducing scan-like vocabulary in the active inventory-progress path.
- This is presentation and review-honesty hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 Final Test-Output Lock - 2026-06-02

A final constrained-sandbox test-output pass was applied after the simulation vocabulary lock:

- `tests/test_packaging.py` now captures `check_frontend_bindings.py` stdout before asserting the result.
- `tests/test_v19_file_inventory.py` now captures `check_file_inventory.py` stdout and parses the JSON payload explicitly.
- Full unittest discovery stays quiet on stdout/stderr except for unittest progress, which makes reviewer logs easier to read and reduces noisy CI output.
- `docs/release/FILE_INVENTORY.json` was regenerated after the test changes.

Verified after this pass:

```txt
python scripts/run_clean_validation.py
Ran 124 tests
OK

python scripts/check_file_inventory.py
status: pass

python scripts/check_release_zip.py
status: pass
errors: []
warnings: []
```

This remains a local safe simulator. The package still does not provide live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring coverage.

## v27 final review-clean lock validation

Additional review-clean pass removed duplicate v26-named current-release gate tests and cleaned `scripts/validate_project.py` formatting/duplicate required-file drift. The current v27 tests remain the source of truth for capability boundary, gate registry, and publication hygiene.

Validation commands run after the review-clean pass:

```bash
python scripts/run_clean_validation.py
python scripts/check_release_zip.py
python scripts/check_file_inventory.py
```

Result: all checks passed. Runtime dependencies were installed in the review sandbox for the full unittest pass; no runtime logs, data folders, bytecode caches, ZIP files, or database artifacts were kept in the release archive.

## v27 final legacy-payload cleanup lock

A final active-frontend vocabulary cleanup removed the legacy `progress.scanned` fallback from `static/dashboard.js`. Current simulator payloads now use only `processed` for sample asset generation progress, and a regression test blocks reintroducing the legacy active-UI field.

This is review-honesty and UI/API vocabulary hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Final release-note identity check

A documentation-only cleanup corrected older release-note lead lines that referenced the wrong version number. The test suite now includes a release-note identity regression check so future handoff packages catch this class of review-confusing documentation drift.

This check does not change simulator behavior or add real packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final Makefile hygiene lock

A final automation hygiene pass removed a duplicate `validation-hygiene` target from the Makefile and added `.PHONY` coverage for the release-matrix/check alias targets. The static safety suite now includes a regression check for duplicate Make targets and missing `.PHONY` declarations.

Validation commands run after this pass:

```bash
python scripts/run_clean_validation.py
python scripts/check_file_inventory.py
python scripts/check_release_zip.py
```

All checks passed. This remains build/reviewer hygiene only and does not add live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final Make target parity lock

A final Makefile parity check found that `.PHONY` listed `validation-hygiene` without a matching target. The target now runs `scripts/check_validation_hygiene.py`, and the static Makefile test now fails on both missing `.PHONY` entries and stale extra `.PHONY` entries.

This is reviewer automation hygiene only. It does not add live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final current-doc language lock

The current-facing README and quick-start wording now refers to the active v27 package for Docker Compose, REST fallback, and validation criteria instead of leaving legacy v18 labels in active feature sections. A static regression test prevents those stale current-doc phrases from returning.


## v27 final test-name alignment lock

A final reviewer-facing test hygiene pass aligned versioned test class and method names with their owning test modules and added regression coverage for future version drift.

Validation commands run after this pass:

```bash
python scripts/run_clean_validation.py
python scripts/check_file_inventory.py
python scripts/check_release_zip.py
```

Observed result: all checks passed after refreshing `docs/release/FILE_INVENTORY.json`. This remains test/readability hygiene only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final test-method drift lock

A final test-readability pass removed an older-version reference from a v17 test method name (`test_manifest_declares_v18_release_note_once`) and strengthened the static safety suite so versioned test modules reject any embedded mismatched `vN` method-name references, not only methods that start with `test_vN_`.

This is reviewer/test hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Final active-doc heading cleanup

A final reviewer-facing documentation pass removed stale historical version labels from active documentation headings in README, quick start, quality-gate, preflight, release-manifest, and final-review checklist files. Historical release notes remain versioned, but current handoff docs now use current/generic headings so reviewers do not confuse old gate names with the active v27 package. A static regression test prevents older v3-v26 headings from returning to active handoff docs.



## Final handoff documentation parity cleanup

A final reviewer-facing parity pass aligned the active handoff documentation with the actual compact default behavior of `scripts/final_handoff_check.py`. The default command delegates to `scripts/run_clean_validation.py`; `--plan` prints the expanded release checklist; explicit release ZIP build/verification remains documented through `scripts/build_release.py` and `scripts/check_release_zip.py`. A static regression test now prevents the old over-specific ZIP-build wording from returning to active handoff docs.

Runtime dependencies were installed in the review sandbox and targeted runtime/API validation paths were verified through the canonical clean validation flow and focused runtime tests. Raw full `unittest discover` is intentionally not the reviewer-facing command because constrained sandboxes can keep non-critical handles alive after importing runtime dependencies. This remains release-handoff hygiene only and does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 release-ID/package-version clarity lock

A final review found one small wording inconsistency: several reviewer-facing docs said the current safe release version was aligned with `pyproject.toml`, even though `pyproject.toml` correctly uses the normalized PEP 440 package version `27.0.0` while the handoff release ID is `27.0.0-safe`.

Fixes applied:

- Clarified the distinction between safe release ID and normalized package version.
- Updated release matrix, release identity, quality gate, API reference, release manifest, README, and final review wording.
- Added a regression test so future edits do not reintroduce misleading `pyproject.toml` release-ID language.

This is metadata/documentation clarity only. It does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final release-ID prefix cleanup lock

A final review found that several active reviewer-facing docs used an extra `v` prefix while the app/API/manifest safe release ID is `27.0.0-safe`. The docs now use the exact safe release ID without the extra `v` prefix, and a static safety regression test prevents this display drift from returning.

Validation commands run after this pass:

```bash
python scripts/run_clean_validation.py
python scripts/check_file_inventory.py
python scripts/check_release_zip.py
```

Observed result: all checks passed after refreshing `docs/release/FILE_INVENTORY.json`. This remains documentation/release-metadata hygiene only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final runtime-route lock

A final runtime-route regression pass verified the reviewer-facing Flask quality endpoints with runtime dependencies installed. `/api/release` now calls a concrete `_release_identity()` helper, and `tests/test_app_runtime.py` covers the full reviewer endpoint set including `/api/release`, `/api/artifact`, `/api/integrity`, `/api/manifest`, `/api/publication`, `/api/gates`, `/api/capabilities`, and `/api/reviewer`. This is runtime/API reliability hygiene only and does not add live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


## Final current release-note ID-prefix hygiene lock

- Removed a remaining literal prefixed safe release ID example from the current `RELEASE_NOTES_v27.md`.
- Extended the static safety test so current release notes are covered by the same no-prefix release ID rule as active handoff documentation.
- Scope unchanged: this remains a local safe simulator with no live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final nested-ZIP hygiene lock

A final release-packaging hygiene pass found that generated caches, logs, databases, and runtime data were blocked, but nested `.zip` files were not fully blocked by both the build and ZIP-inspection paths. The builder now excludes `.zip` files, the ZIP inspector rejects nested archive members, and the release-artifact service treats nested ZIP files as blocking handoff artifacts.

Validation coverage added:

- build-time test confirming stray `.zip` files are excluded from generated release archives;
- inspect-time test confirming a ZIP containing a nested `.zip` member fails validation;
- static safety test confirming the release builder, ZIP inspector, and artifact gate all recognize `.zip` as a blocked release artifact.

This is release-packaging hygiene only. Scope unchanged: the project remains a local safe simulator with no live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final versioned-test release-note reference lock

A final review found that a few versioned test modules still referenced unrelated historical release-note filenames in string assertions. This did not affect runtime behavior, but it could confuse reviewers reading the tests.

Fixes applied:

- `test_v11_quality.py` now validates preflight files without requiring historical root release notes.
- `test_v11_quality_gate.py` now validates quality-gate files without requiring historical root release notes.
- `test_v17_release_zip.py` now checks that the manifest exposes only the current `RELEASE_NOTES_v27.md` entry.
- `tests/test_static_safety.py` now rejects unrelated `RELEASE_NOTES_vM.md` references inside `test_vN_*` modules, while still allowing the current `RELEASE_NOTES_v27.md` reference where appropriate.

Validation commands run after this pass:

```bash
python scripts/run_clean_validation.py
python scripts/check_file_inventory.py
python scripts/check_release_zip.py
```

Observed result: all checks passed after refreshing `docs/release/FILE_INVENTORY.json`. This remains reviewer/test hygiene only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


## Test runner lock validation

- Updated `make test` and current docs to use `scripts/run_clean_validation.py` instead of raw `unittest discover`.
- This keeps reviewer validation deterministic and avoids sandbox-specific post-test hangs after runtime dependency checks.

## v27 final validation-documentation command lock

A final review found that the current validation report still preserved several raw full-discovery commands from earlier audit snapshots. The official reviewer command is now consistently `python scripts/run_clean_validation.py`, and a static regression test now checks README, INSTALL_CHECK, the current validation report, and current release notes for raw full-discovery command drift.

This is validation-documentation hygiene only. Scope unchanged: the package remains a local safe simulator with no live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## v27 Final Environment Example Comment Hygiene Lock

A final active setup-example pass removed stale `Docker Compose v13` wording from `.env.example`. The password requirement applies to the current Docker Compose setup and should not look tied to a historical release phase.

Validation added:

- `test_current_runtime_examples_do_not_reference_legacy_release_labels` checks current setup/deployment examples for legacy release labels in active guidance.
- `python scripts/run_clean_validation.py` passed after the update.
- `python scripts/check_file_inventory.py` passed after refreshing `docs/release/FILE_INVENTORY.json`.
- `python scripts/check_release_zip.py` passed on the rebuilt release ZIP.

This is documentation/reviewer hygiene only. Scope unchanged: the package remains a local safe simulator with no live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## Active Doc Legacy Label Cleanup Validation

- Active architecture documentation no longer presents earlier internal iteration labels as current handoff wording.
- `scripts/check_schema_contract.py` now describes the current schema contract instead of an older gate number.
- Static safety tests include active-doc/script legacy-label regression coverage.

## Final review-command alignment check

A final reviewer-command audit aligned README, DEPLOYMENT, INSTALL_CHECK, the final-review checklist, and the quick-start checklist with the canonical clean validation command, `python scripts/run_clean_validation.py`. `scripts/validate_project.py` remains an internal gate used by the wrapper, but active reviewer instructions no longer present it as the primary command.

Observed result: clean validation and release ZIP checks passed after refreshing `docs/release/FILE_INVENTORY.json`. This remains documentation/reviewer workflow hygiene only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


## v27 final reviewer-command parity lock

A final command-parity pass removed stale primary `python scripts/validate_project.py` instructions from active reviewer-facing docs. Reviewers should use `python scripts/run_clean_validation.py`; `validate_project.py` remains an internal gate called by the wrapper. Static safety tests now cover README, DEPLOYMENT, INSTALL_CHECK, quick start, and final review docs so this command drift does not return.

Scope unchanged: this is a safe local simulator package only and does not add live packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## CI command parity lock

The CI workflow and packaging tests were aligned with the canonical clean validation command. `validate_project.py` remains an internal gate only; reviewer-facing CI/docs/tests now point at `python scripts/run_clean_validation.py`.
## FINAL_MAKEVALIDATE_LOCKED validation

- `make validate` now uses the canonical clean validation wrapper: `python scripts/run_clean_validation.py`.
- The direct project gate remains available as `make project-validate` for maintainers.
- Static safety tests now assert that both `make test` and `make validate` use the clean validation runner.

## Final runtime data directory lock

A runtime-enabled full-test audit found that constructing `IPv6SentinelApp` could create the default `data/` directory before tests redirected paths to a temporary folder. Because release-artifact checks intentionally treat runtime data as handoff pollution, this could make `/api/quality`, `/api/artifact`, and release-audit tests fail later in the same session. `IPV6_SENTINEL_DATA_DIR` now controls the runtime data directory, and runtime tests set it before app construction.


## Final validation-exit lock

Direct `scripts/validate_project.py` now flushes stdout/stderr and exits explicitly after validation returns. This keeps the lower-level gate from hanging in constrained review sandboxes after runtime/validation imports while preserving `python scripts/run_clean_validation.py` as the canonical reviewer command.


## Final full-test runner lock

A final validation-exit follow-up added `scripts/run_full_tests.py` as an optional full unittest sweep. The canonical reviewer command remains `python scripts/run_clean_validation.py`, while the new full-test runner executes the full unittest discovery inside one bounded subprocess with bytecode disabled, runtime logging disabled, and a temporary data directory. This improves review repeatability only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Final full-test cleanup parity lock

A follow-up audit found that nested-ZIP regression tests could leave a stray `.zip` file behind if a constrained test process was interrupted before `finally` cleanup ran. `scripts/clean_release_artifacts.py` now treats stray `.zip` files as generated release artifacts, so clean validation and the optional full-test runner start from a clean source tree even after interrupted tests. This improves release hygiene only and does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## v27 final local-venv validation lock

A final validation-path correction was applied for the README's normal local setup flow:

- `scripts/check_release_artifact.py` now ignores local reviewer tooling folders such as `.venv/` during source-tree checks.
- Built ZIP validation and `scripts/build_release.py` still reject/exclude virtualenv folders from the handoff archive.
- A regression test covers the common flow: create `.venv/` in the project root, install `requirements.txt`, then run the project validation gates.

This is release-workspace hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## v27 final full-test runner isolation lock

The optional `scripts/run_full_tests.py` command now runs the full unittest discovery set in one bounded child process with heartbeat output and process-group timeout cleanup. This preserves full-suite coverage while avoiding repeated interpreter-spawn stalls in constrained sandboxes.

This is test-runner hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Final claim-tone polish validation

A final wording audit removed remaining reviewer-facing legacy policy-action wording from Korean UI/documentation labels where the app only shows a simulated policy response. The simulator metric/API name now uses policy-response wording so the code, API payload, and displayed UI all avoid implying real blocking action. Scope unchanged: this remains a safe local simulator and does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## Final clean-validation subprocess exit lock

A final reviewer-runner audit found that `scripts/run_clean_validation.py` could appear to hang in constrained sandboxes when it captured child process pipes directly from `scripts/validate_project.py`. The child validation completed successfully, but inherited pipe handles could delay EOF in the wrapper. The clean validation wrapper now redirects each step to temporary files, runs each step in its own process group, and kills that process group on timeout.

Observed validation after the update:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass
- `python scripts/run_full_tests.py` -> pass, 138 tests observed across 21/21 modules
- `python scripts/check_release_zip.py` -> pass

This is validation-runner hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## v27 Final Full-Test PIPEWAIT Lock

A post-runner-exit audit found one remaining constrained-sandbox hang vector: `scripts/validate_project.py` used direct stdout/stderr PIPE capture when running its internal unittest modules. The validation completed logically, but inherited pipe handles from non-critical descendants could keep the parent waiting for EOF in some review environments.

The validator now uses the same safer pattern as the clean wrapper: temporary file-backed child output, `start_new_session=True`, `proc.wait(timeout=...)`, and process-group cleanup with `os.killpg()` on timeout. This keeps both `python scripts/validate_project.py` and `python scripts/run_clean_validation.py` deterministic while preserving the safe-simulation capability boundary.

## v27 Final Full-Test PIPEWAIT-2 Lock

A follow-up validation run found two additional pipe-capture paths inside `scripts/validate_project.py`: the final handoff plan check and reviewer handoff check. They were short script calls, but in constrained sandboxes any inherited pipe capture can still delay EOF. These checks now load the relevant modules directly instead of spawning pipe-captured subprocesses. A regression test now asserts that `validate_project.py` does not use `capture_output=True` or unittest stdout/stderr PIPE capture for its internal validation path.

## v27 Final Full-Test PROCESSRETURN Lock

A short-lived process-return experiment removed forced top-level exits after pipe-capture hardening. Later FORCEDRETURN/OSWRITE locks superseded that approach: the current reviewer wrappers bound their child-process groups, write final JSON with `os.write()`, and then exit via `os._exit()` to avoid interpreter-shutdown waits in constrained review shells.

## v27 Final Full-Test DIRECTCLEAN Lock

`run_clean_validation.py` now performs the deterministic clean-before, clean-after, and validation-hygiene steps in-process while keeping the heavier `validate_project.py` step in a bounded child process. This removes the last avoidable subprocess wait point from the canonical reviewer command while preserving process-group timeout cleanup for the only step that needs child isolation.

## v27 Final Full-Test FORCEDRETURN Lock

The canonical validation wrappers keep the child-process waits bounded and then use a flushed `os._exit()` at the top-level script boundary. This avoids Python interpreter-shutdown waits from non-critical imported dependencies after the JSON result has already been written.

## v27 Final Full-Test OSWRITE Lock

The reviewer validation wrappers now write their final JSON payload through `os.write()` and then call `os._exit()` at the script boundary. This avoids both pipe-capture waits and interpreter-shutdown waits after all child validation steps have completed.

## v27 Final Full-Test POLICYAPI Lock

A final API/code terminology audit found that the user-facing UI already said “policy response,” but internal API/stat/settings names still used legacy block-oriented stat, setting, and event keys. Those names could make a reviewer think the simulator performs a real network blocking action.

The simulator now uses policy-response naming consistently across app code, schema contract, settings payload, dashboard bindings, and runtime tests:

- `policy_response_events`
- `policy_response_enabled`
- `policy_response_simulated`

A static regression test prevents the legacy block-oriented simulator API names from returning in active code/UI paths. Scope remains unchanged: this is a safe local simulator and does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

### Final full-test runner polling lock

- Updated `scripts/run_full_tests.py` to wait for one bounded unittest discovery child with a polling loop and heartbeat output instead of repeatedly spawning isolated modules.
- Kept file-backed stdout/stderr capture, per-module temporary data roots, `start_new_session=True`, and process-group timeout cleanup.
- Added regression coverage so the optional full-test runner stays responsive in constrained reviewer environments.
- Capability boundary unchanged: no live IPv6 packet capture, packet sending, scanning, spoofing, or production blocking/detection capability was added.
## v27 Final Full-Test TIMEOUTIMPORT validation

A final timeout-path audit confirmed that the optional full-test runner imports `contextlib` before using `contextlib.suppress()` in the process-group timeout cleanup branch. Remaining legacy policy-action wording in current reviewer-facing docs was also rephrased to avoid implying any real blocking capability. Scope remains unchanged: safe local simulation only.
## v27 CDNTERM final wording lock

- Removed the last Korean demo heading that could read as a generic “block” claim by changing it to a CDN access-restriction fallback note.
- Re-ran core validation, clean validation, release ZIP inspection, publication hygiene, and capability boundary checks after the wording-only patch.
- Capability boundary remains unchanged: no packet capture, packet sending, network scanning, or real blocking capability.


## v27 Final Full-Test SUBPROCTIMEOUT validation

A final test-runner audit added explicit timeout bounds to test subprocess calls and added regression coverage to prevent new unbounded test subprocesses. The optional full-test runner now keeps a shorter per-module timeout while the canonical handoff command remains `python scripts/run_clean_validation.py`.

Observed after the update:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass
- `python scripts/run_full_tests.py` -> pass, full unittest discovery observed 154/155 tests across 21/21 discovered modules depending on runtime dependency availability

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 Final Full-Test VENVCOMPILE validation

A final reviewer-workspace validation pass was run with a local virtual environment present under the project root. The previous validator skipped virtualenvs in release-artifact checks but still used whole-tree Python compilation, which could make `python scripts/validate_project.py` slow or appear stuck after README-style environment setup.

Updated validation behavior:

- `scripts/validate_project.py` compiles project-owned Python files only.
- Workspace scanners now consistently skip `.venv/`, `venv/`, `env/`, `.testvenv/`, and `node_modules/` where applicable.
- Release ZIP and build checks still prevent virtualenv content from entering handoff archives.
- Regression tests assert that whole-tree `compileall.compile_dir(str(ROOT))` is not reintroduced and that workspace scanners know the reviewer virtualenv names.

Observed after the update:

- `python scripts/validate_project.py` -> pass with a root-level local virtualenv present
- `python scripts/run_clean_validation.py` -> pass
- `python scripts/run_full_tests.py` -> pass
- `python scripts/check_release_zip.py` -> pass

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 Final Full-Test WALKPRUNE validation

A follow-up validation pass confirmed that source-tree scanners should not merely filter virtualenv paths after recursive discovery; they should prune local reviewer workspace directories before traversal. The relevant cleanup, build, validation, inventory, release-artifact, publication-hygiene, capability-boundary, diagnostics, quality-gate, and static-safety paths now use pruned `os.walk(...)` traversal where reviewer virtualenvs may exist under the project root.

Observed after the update:

- validation works with a root-level `.testvenv/` present
- clean/build/inventory scans do not descend into reviewer virtualenv folders
- regression tests assert that the key workspace scanners use pruned walking

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 final full-test spawn-hang follow-up

A final reviewer-runner pass found that repeatedly spawning one Python interpreter per test module could still stall at process creation in constrained sandboxes, even when the same tests passed individually. `scripts/run_full_tests.py` now runs one bounded unittest discovery child with heartbeat output, file-backed logs, disabled bytecode/runtime logs, temporary runtime data, and process-group timeout cleanup. The canonical quick check remains `python scripts/run_clean_validation.py`. This change only improves validation runner reliability and does not add live IPv6 packet capture, packet sending, network scanning, IDS, IPS, or production monitoring capability.


## v27 Final Full-Test DOCSYNC validation

A final documentation synchronization pass updated the recorded full-test observation count after rerunning `python scripts/run_full_tests.py` in an environment with runtime dependencies installed. The optional full-test runner now reports 154/155 observed tests across 21/21 discovered modules depending on runtime dependency availability in this validation environment.

Observed after the update:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass
- `python scripts/run_full_tests.py` -> pass, full unittest discovery observed 154/155 tests across 21/21 discovered modules depending on runtime dependency availability
- `python scripts/check_release_zip.py` -> pass

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 Final Full-Test SUITESETTLE validation

A final optional full-test runner validation found that some constrained review shells can leave the unittest discovery child alive briefly after the final `OK` summary has already been written to the file-backed stderr log. `scripts/run_full_tests.py` now recognizes the final unittest summary, waits a short settle window, and then cleans the child process group while preserving the printed pass/fail result.

Validation results in this dependency-light review environment:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks
- `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules, 20 skipped runtime-dependency tests
- `python scripts/check_release_zip.py` -> pass

The optional full-test count is environment-sensitive: dependency-light runs can observe 154 tests with runtime-dependent tests skipped, while dependency-installed runs can observe 155. The capability boundary is unchanged: no live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability is added.
## v27 Final Full-Test DOCEXIT validation

A final documentation-exit audit removed stale wording from the PROCESSRETURN snapshot that incorrectly described the current wrappers as returning through normal `SystemExit`. The active implementation and current documentation now agree: validation wrappers use bounded child-process groups, final `os.write()` payload output, and top-level `os._exit()` to avoid interpreter-shutdown waits after validation has completed.

Observed checks after the update:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks
- `python scripts/run_full_tests.py` -> pass, 155 tests observed across 21/21 discovered modules in the runtime-dependency-installed validation environment
- `python scripts/check_release_zip.py` -> pass with no errors or warnings

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 Final Full-Test DEPSCOUNT validation

A final dependency-count synchronization pass confirmed that the optional full-test runner count is environment-sensitive:

- dependency-light validation: `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules, 20 runtime-dependency tests skipped
- runtime-dependency-installed validation: `python scripts/run_full_tests.py` -> pass, 155 tests observed across 21/21 discovered modules, 0 skipped
- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks
- `python scripts/check_release_zip.py` -> pass with no errors or warnings

This is documentation synchronization only. Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.


## PIPEFREE validation update

A final reviewer-environment hardening pass moved test-internal project script checks away from `subprocess.run(capture_output=True)` and into a shared `tests/process_helpers.py` helper. Project-local Python scripts are now executed in-process with captured stdout/stderr, while a file-backed process-group fallback remains available for non-project commands. This avoids pipe/EOF waits in constrained sandboxes and keeps `python scripts/run_full_tests.py` fast and bounded.

Validation observed after this change:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks passed
- `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules in dependency-light mode, 20 runtime-dependency tests skipped
- `python scripts/check_release_zip.py` -> pass, no errors or warnings

This is test-runner hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## PIPEFREE count synchronization

After adding the pipe-free test helper regression check, the dependency-light validation count is now 154 observed tests across 21/21 discovered modules with 20 runtime-dependency tests skipped. A runtime-dependency-installed environment is expected to observe 155 tests with the runtime tests active. The verified dependency-light run completed quickly with `Ran 154 tests in 3.975s` and `OK (skipped=20)`.

This count update is documentation/report synchronization only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.


## PIPEFREE count-span synchronization

A final count-span audit confirmed the current expected optional full-test span is `154/155`, not the older stale older 148-to-149 wording. In this dependency-light environment, `python scripts/run_full_tests.py` reports 154 tests with 20 runtime-dependency tests skipped. In the runtime-dependency-installed environment, the same command reports 155 tests with no skips. This update is documentation and regression-test hygiene only; it does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## CDN fallback wording validation

A final active-document wording audit removed the remaining English legacy CDN block-oriented wording from current reviewer-facing docs. Active CDN fallback documentation now uses “CDN access is restricted” / “CDN-restricted” wording. A regression test protects this wording, so the optional full-test span is now `154/155`: dependency-light environments observe 154 tests with runtime-dependent tests skipped, and runtime-dependency-installed environments observe 155 tests with no skips. Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.


## v27 Final Full-Test COUNTDOCNORMAL validation

A final count-documentation audit corrected stale historical lines that paired `154 tests observed` with `20 skipped runtime-dependency tests` or described 154 tests as dependency-light mode. The current expected span is now consistently documented:

- dependency-light validation: `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules, 20 runtime-dependency tests skipped
- runtime-dependency-installed validation: `python scripts/run_full_tests.py` -> pass, 155 tests observed across 21/21 discovered modules, 0 skipped
- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks
- `python scripts/check_release_zip.py` -> pass with no errors or warnings

This is documentation and regression-test hygiene only. Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.


## PROCESSHELPER_EXITGUARD validation
A final review found that the shared pipe-free test helper could theoretically execute project scripts containing `os._exit()` in-process. The helper now detects those scripts and falls back to the file-backed process-group subprocess path. Regression coverage was added so `run_full_tests.py` remains protected from accidental test-process termination.


## PROCESSHELPER_EXITGUARD count sync
After adding the process-helper exit-guard regression test, `python scripts/run_full_tests.py` reports 154 tests in the dependency-light environment with 20 runtime-dependent tests skipped. A runtime-dependency-installed environment is expected to observe 155 tests with no skips.

## DOCREVIEW validation

Final whole-package review found one documentation/UX mismatch: active reviewer commands still referenced `python -m compileall -q .`, which can traverse a reviewer-created `.venv` and contradicts the pruned validation path. The active README and Makefile now route reviewers through `python scripts/run_clean_validation.py` and optional `python scripts/run_full_tests.py` instead. The Korean CDN fallback wording was also normalized to an access-restricted phrasing.


After this DOCREVIEW pass, the runtime-dependency-installed full sweep observed 155 tests. Dependency-light reviewers are expected to observe 154 tests with the runtime-dependent tests skipped.

## WINPATH validation

- Added a cross-platform path-normalization guard for release artifact checks.
- `services/release_artifact.py` now compares required handoff files with `Path.as_posix()` relative paths instead of OS-native separators.
- This addresses Windows PowerShell validation failures where forward-slash manifest paths and backslash `Path` strings could disagree.
- `python scripts/run_full_tests.py` -> pass after WINPATH guard, dependency-light environments should observe 154 tests with 20 skips and runtime-dependency-installed environments should observe 155 tests with no skips.

## Windows validation process-control hardening

A final Windows-focused reviewer pass replaced runner-local POSIX-only timeout cleanup with the shared `services/process_control.py` helper. `validate_project.py`, `run_clean_validation.py`, `run_full_tests.py`, and the unittest process helper now call portable subprocess-isolation and timeout-cleanup functions. POSIX still uses a new child session; Windows uses `CREATE_NEW_PROCESS_GROUP` when available and then terminate/kill fallback cleanup on timeout. This only hardens reviewer validation commands and does not change the safe local simulation boundary.

## Fresh clone note

File inventory validation uses LF-normalized text hashing so a clean Git clone on Windows/macOS/Linux should produce the same inventory digest when the file content is otherwise unchanged.
