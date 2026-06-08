# Release Notes v27

## Focus

v27 is a reviewer-handoff polish release. It does not add live IPv6 monitoring capability. It makes the package easier to review honestly before GitHub upload or portfolio submission.

## Changes

- Added `/api/reviewer` as a single review-oriented summary endpoint.
- Added `services/reviewer_handoff.py`.
- Added `scripts/check_reviewer_handoff.py`.
- Added `docs/quality/REVIEWER_HANDOFF.md`.
- Added reviewer handoff to the quality gate, gate registry, manifest, OpenAPI, API reference, CI, and validation flow.
- Updated version metadata to `27.0.0-safe`.

## Honest limitation

This remains a local educational simulator. It still does not capture packets, send packets, scan networks, or provide IDS/IPS detection coverage.

### Final audited packaging note

- Tightened unittest hygiene by removing duplicate test class names and ensuring direct test-module execution does not skip later classes.
- Added static regression checks for test class uniqueness and `unittest.main()` placement.
- Refreshed the deterministic file inventory after this final audit.

### Final unittest-discovery correction

- Converted reviewer handoff tests from module-level functions into a `unittest.TestCase`.
- Added a static regression check that blocks module-level `test_*` functions in unittest-based test modules.

### Final audited privacy pass

- Masked local IPv4, IPv6, and MAC values in runtime configuration logs.
- Added a static safety assertion for masked configuration logging.
- No new live network capability was added; the project remains a local safe simulator.

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

- Renamed the active sample-inventory progress payload from `scanned` to `processed`.
- Renamed the decorative dashboard CSS animation from `scan` to `safeSweep`.
- Added a static safety regression test for the active inventory-progress vocabulary.
- This is review-honesty/UI hygiene only and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final test-output lock addendum

- Captured stdout for helper scripts that are invoked directly from unit tests.
- This keeps full `unittest discover` output quiet and review-friendly while still asserting the helper payloads.
- Refreshed the deterministic file inventory after this test harness change.
- This is test-output hygiene only and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

### v27 final review-clean lock

- Removed duplicate v26-named gate test files that repeated the current v27 capability, gate registry, and publication hygiene checks.
- Added a static regression test to keep legacy-named duplicate current-release gate tests out of the handoff package.
- Cleaned a duplicate `RELEASE_NOTES_v27.md` entry and indentation drift in `scripts/validate_project.py`.
- No capability changes: the package remains a local safe simulator, not a live IPv6 scanner, sniffer, IDS/IPS, or packet tool.

## v27 final legacy-payload cleanup lock

A final active-frontend vocabulary cleanup removed the legacy `progress.scanned` fallback from `static/dashboard.js`. Current simulator payloads now use only `processed` for sample asset generation progress, and a regression test blocks reintroducing the legacy active-UI field.

This is review-honesty and UI/API vocabulary hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 release-note identity cleanup lock

A final documentation consistency pass corrected legacy release-note lead lines whose opening summaries referenced a later version number. A regression test now verifies that each `RELEASE_NOTES_vN.md` file starts with the matching `vN` identity in its first prose line.

This is documentation hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final Makefile hygiene lock

A final reviewer-facing automation cleanup removed a duplicate `validation-hygiene` Make target and added the missing `.PHONY` declarations for release-matrix/check alias targets. A static regression test now verifies Makefile targets are unique and fully covered by `.PHONY`.

This is build-script/reviewer hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final Make target parity lock

- Added the missing `validation-hygiene` Make target so every `.PHONY` entry maps to a real target.
- Strengthened the Makefile static test to reject both missing `.PHONY` declarations and stale extra `.PHONY` entries.
- This is automation/reviewer hygiene only and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final current-doc language lock

The current-facing README and quick-start wording now refers to the active v27 package for Docker Compose, REST fallback, and validation criteria instead of leaving legacy v18 labels in active feature sections. A static regression test prevents those stale current-doc phrases from returning.


## v27 final test-name alignment lock

A final reviewer-facing test hygiene pass aligned versioned test class and method names with their owning test modules. Examples include old `V13...` class names in `test_v11_*` modules and old `V18...` class names in `test_v16_*`/`test_v19_*` modules. The static safety suite now blocks future version drift in version-prefixed test class and test method names.

This is test/readability hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final test-method drift lock

A final test-readability pass removed an older-version reference from a v17 test method name (`test_manifest_declares_v18_release_note_once`) and strengthened the static safety suite so versioned test modules reject any embedded mismatched `vN` method-name references, not only methods that start with `test_vN_`.

This is reviewer/test hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Final active-doc heading cleanup

A final reviewer-facing documentation pass removed stale historical version labels from active documentation headings in README, quick start, quality-gate, preflight, release-manifest, and final-review checklist files. Historical release notes remain versioned, but current handoff docs now use current/generic headings so reviewers do not confuse old gate names with the active v27 package. A static regression test prevents older v3-v26 headings from returning to active handoff docs.


## v27 final handoff-doc parity lock

A final reviewer-facing documentation cleanup aligned `scripts/final_handoff_check.py` with the active README, final handoff doc, review checklist, and release manifest. The default handoff command is now documented as a compact `run_clean_validation.py` wrapper, while `--plan` is documented as the expanded checklist view and explicit ZIP validation stays with `scripts/build_release.py` plus `scripts/check_release_zip.py`.

This is documentation/script parity only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 release-ID/package-version clarity lock

A final documentation and gate-message pass clarified that the reviewer-facing safe release ID is `27.0.0-safe`, while `pyproject.toml` intentionally uses the normalized PEP 440 package version `27.0.0`. This prevents reviewers from reading the release matrix as a contradiction between package metadata and the safe handoff ID.

- Updated release identity, release matrix, quality gate, API reference, release manifest, and final review wording.
- Added a static regression test to prevent future docs from claiming that `pyproject.toml` contains the hyphenated safe release ID.
- No capability changes: this remains a local safe simulator and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final release-ID prefix cleanup lock

A final documentation pass standardized reviewer-facing references to the safe release ID as `27.0.0-safe` without the extra `v` prefix. This keeps README and active handoff docs visually aligned with API payloads, `project_manifest.json`, OpenAPI, validation reports, and service constants.

- Replaced the previously prefixed safe release ID variant with `27.0.0-safe` across active documentation.
- Added a static regression test to prevent the prefixed form from returning in current handoff docs.
- No capability changes: this remains a local safe simulator and does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## Runtime route regression lock

A final runtime-route regression pass fixed `/api/release`, which was documented and declared but could return 500 because the Flask handler referenced a missing `_release_identity()` helper. The runtime route test now covers all reviewer-facing quality endpoints so documented API routes cannot silently drift from executable Flask handlers.


## Final current release-note ID-prefix hygiene lock

A final documentation hygiene pass removed the literal prefixed safe release ID example from the current v27 release notes and replaced it with a descriptive phrase. A regression test now covers the current release notes as well as active handoff docs so the safe release ID stays aligned with API and manifest payloads.

This is documentation/reviewer hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final nested-ZIP hygiene lock

A final release-packaging hygiene pass closed a nested-archive gap: the release builder now excludes `.zip` files, the ZIP inspector rejects nested `.zip` members, and the release-artifact gate treats nested ZIP files as blocking handoff artifacts instead of soft warnings. Regression tests cover both build-time exclusion and inspect-time rejection.

This is release-packaging hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final versioned-test release-note reference lock

A final reviewer-facing cleanup removed historical root release-note files before v27 from the public handoff. Versioned tests now validate the current release-note manifest instead of requiring old root-level notes, keeping the GitHub file list focused on the final package.

This is test/readability hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


## Test runner lock

- Updated `make test` and current docs to use `scripts/run_clean_validation.py` instead of raw `unittest discover`.
- This keeps reviewer validation deterministic and avoids sandbox-specific post-test hangs after runtime dependency checks.

## Final validation-documentation command lock

- Replaced remaining current validation-report examples of raw full `unittest discover` commands with the canonical `python scripts/run_clean_validation.py` wrapper.
- Added a static safety regression test that blocks raw full-discovery command recommendations in current reviewer-facing docs.
- Added a static safety regression test that detects duplicate test method names inside a unittest class, preventing silent method shadowing.
- Scope unchanged: this remains a safe local simulator and does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## Environment Example Comment Hygiene Lock

A final active environment-example cleanup removed a stale `Docker Compose v13` wording from `.env.example`. The current Docker Compose password requirement is not version-specific, so the example now says Docker Compose requires the password value explicitly. A static regression test now blocks current runtime/deployment examples from reintroducing legacy release labels in active setup guidance.

This is documentation/reviewer hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
## Active Doc Legacy Label Cleanup

- Replaced stale internal-iteration labels in active architecture and schema-checker text with current-package wording.
- Added regression coverage so active non-history docs/scripts do not reintroduce v3-v26 labels outside explicit release-note history.

## Final review-command alignment

A final reviewer-command cleanup aligned the active final-review checklist and quick-start checklist with the canonical clean validation command, `python scripts/run_clean_validation.py`. The static safety suite now checks these active reviewer-facing documents so stale `python scripts/validate_project.py` primary-check instructions do not reappear.

This is documentation/reviewer workflow hygiene only. It does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


## Final reviewer-command parity lock

Active reviewer-facing docs now consistently present `python scripts/run_clean_validation.py` as the canonical validation command. `scripts/validate_project.py` remains an internal gate used by the clean wrapper, but README/DEPLOYMENT/checklists no longer present it as the primary reviewer command.
## CI command parity lock

- CI workflow comments and packaging tests now assert the canonical `python scripts/run_clean_validation.py` reviewer command instead of passing via a stale `python scripts/validate_project.py` comment.
- Added a static safety check so CI cannot reintroduce `validate_project.py` as the reviewer-facing primary command.
## v27 final make validate parity lock

v27 final make validate parity lock aligns reviewer-facing Makefile targets with the canonical clean validation path. `make validate` now runs `scripts/run_clean_validation.py`, while `make project-validate` remains available for the internal lower-level `scripts/validate_project.py` gate. This prevents reviewers from seeing two different default validation paths.

### Final runtime data directory lock

Runtime app construction now respects `IPV6_SENTINEL_DATA_DIR`, and runtime tests set that value before constructing the Flask app. This prevents runtime-enabled test passes from creating a default source-tree `data/` directory that can make release-artifact and quality gates fail later in the same test session. The change is test/release hygiene only; it does not add live IPv6 monitoring, scanning, packet capture, or packet transmission.

## v27 final validation-claim lock

A final validation-report wording pass removed a stale claim that raw full `unittest discover` was the preferred successful reviewer path after runtime dependencies were installed. Current reviewer guidance remains centered on `python scripts/run_clean_validation.py`, with focused runtime/API checks used where needed. A static regression test now prevents the validation report from reintroducing that raw-discovery claim as the default path.

This is documentation/validation-hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final validation-exit lock

A final validation-runner pass made direct `scripts/validate_project.py` exits explicit after stdout/stderr flush. This keeps lower-level project validation from hanging in constrained review sandboxes after importing runtime/validation dependencies. The canonical reviewer command remains `python scripts/run_clean_validation.py`.

This is validation-runner hygiene only. It does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.


### Final full-test runner lock

- Added `scripts/run_full_tests.py` as an optional bounded full unittest runner with process-group timeout cleanup and short progress output.
- Kept `python scripts/run_clean_validation.py` as the official quick reviewer handoff command.
- Added a `make full-test` target for reviewers who want the complete test sweep without raw `unittest discover` behavior.
- Scope remains unchanged: this is a safe local simulator package only.

### Final full-test cleanup parity lock

- Updated `scripts/clean_release_artifacts.py` to remove stray `.zip` files left by interrupted local test runs.
- Strengthened static safety tests so the cleaner keeps nested ZIP cleanup coverage.
- Scope remains unchanged: this is a safe local simulator package only.

## v27 final local-venv validation lock

- `check_release_artifact.py` now ignores local reviewer `.venv/` workspaces during source-tree validation while release ZIP checks still exclude virtualenv content from handoff archives.
- Added a regression test for the README-style workflow: create `.venv/`, install dependencies, then run validation.
- No capability changes: this remains a local safe simulator, not a live IPv6 scanner, sniffer, IDS/IPS, or packet tool.
## v27 final full-test runner isolation lock

The optional `scripts/run_full_tests.py` command now runs the full unittest discovery set in one bounded child process with heartbeat output and process-group timeout cleanup. This preserves full-suite coverage while avoiding repeated interpreter-spawn stalls in constrained sandboxes.

This is test-runner hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.

## v27 final claim-tone polish

A final wording audit changed remaining reviewer-facing Korean UI/documentation labels from legacy policy-action phrasing to “policy response” phrasing where no real blocking action occurs. This reduces overclaim risk while preserving the updated policy-response simulation metric/API contract. This is UI/documentation claim-tone hygiene only; it does not add packet capture, packet sending, scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## v27 final clean-validation subprocess exit lock

A final reviewer-runner audit found that `scripts/run_clean_validation.py` could appear to hang in constrained sandboxes when it captured child process pipes directly from `scripts/validate_project.py`. The child validation completed successfully, but inherited pipe handles could delay EOF in the wrapper. The clean validation wrapper now redirects each step to temporary files, runs each step in its own process group, and kills that process group on timeout.

Observed validation after the update:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass
- `python scripts/run_full_tests.py` -> pass, full unittest discovery observed 154/155 tests across 21/21 discovered modules depending on runtime dependency availability
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

The final claim-tone pass now removes block-oriented simulator API names from active code/UI/schema paths. The local simulator uses policy-response wording consistently:

- `policy_response_events`
- `policy_response_enabled`
- `policy_response_simulated`

A static regression test prevents legacy block-oriented stat, setting, and event keys from returning in active simulator paths. This is naming honesty only; it does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

### Final full-test runner polling lock

- Updated `scripts/run_full_tests.py` to wait for one bounded unittest discovery child with a polling loop and heartbeat output instead of repeatedly spawning isolated modules.
- Kept file-backed stdout/stderr capture, per-module temporary data roots, `start_new_session=True`, and process-group timeout cleanup.
- Added regression coverage so the optional full-test runner stays responsive in constrained reviewer environments.
- Capability boundary unchanged: no live IPv6 packet capture, packet sending, scanning, spoofing, or production blocking/detection capability was added.
## v27 Final Full-Test TIMEOUTIMPORT Lock

A final timeout-path audit added the missing `contextlib` import used by the optional full-test runner's process-group timeout cleanup path. This is runner hygiene only and does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.
### v27 CDNTERM final wording lock

- Reworded the Korean demo fallback heading from a CDN “block” expression to a CDN access-restriction expression, keeping the project claim surface aligned with the simulation-only policy-response language.
- No runtime capability was added; this remains a local safe simulator with no packet capture, packet sending, scanning, or real blocking capability.


## v27 Final Full-Test SUBPROCTIMEOUT Lock

A final optional full-test audit found that some unittest modules launch helper scripts such as release-audit, preflight, manifest, and handoff checks. Those helper calls now use explicit `timeout=30` bounds in test subprocess invocations, and a regression test scans the test suite to prevent future unbounded `subprocess.run(...)` calls. The optional `scripts/run_full_tests.py` discovery timeout is bounded and emits heartbeat output so constrained reviewer environments show visible progress instead of appearing stuck.

This is test-runner hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## v27 Final Full-Test VENVCOMPILE Lock

A final reviewer-workspace audit found that `scripts/validate_project.py` ignored local virtualenv folders for several source-tree checks, but its final Python compilation step still used a whole-tree compile call. If a reviewer created `.venv/` or `.testvenv/` inside the project root, validation could spend time compiling third-party site-packages instead of only project-owned Python files.

The validator now compiles only project source files and consistently skips reviewer workspace folders such as `.venv/`, `venv/`, `env/`, `.testvenv/`, and `node_modules/` across source scanners and cleanup helpers. Release ZIP checks and build scripts still exclude those local workspace folders from handoff archives.

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

## v27 Final Full-Test WALKPRUNE Lock

A follow-up reviewer-workspace audit tightened the virtualenv skip logic from “filter after `Path.rglob()` yields paths” to pruned `os.walk(...)` traversal for the cleanup, build, validation, inventory, release-artifact, publication-hygiene, capability-boundary, diagnostics, quality-gate, and static-safety scans. This prevents validators and builders from descending into local reviewer folders such as `.venv/` or `.testvenv/` in the first place.

Scope remains unchanged: safe local simulation only; no packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability was added.

### v27 final full-test spawn-hang follow-up

A final reviewer-runner pass found that repeatedly spawning one Python interpreter per test module could still stall at process creation in constrained sandboxes, even though the individual tests passed. `scripts/run_full_tests.py` now runs one bounded unittest discovery child with heartbeat output, file-backed logs, disabled bytecode/runtime logs, temporary runtime data, and process-group timeout cleanup. This is a reviewer-experience fix only; it does not add live IPv6 packet capture, packet sending, network scanning, IDS, IPS, or production monitoring capability.


## v27 Final Full-Test DOCSYNC Lock

A final documentation synchronization pass updated the recorded optional full-test observation count to match the latest dependency-installed validation run: `python scripts/run_full_tests.py` reports 154/155 observed tests across 21/21 discovered modules depending on runtime dependency availability. This is documentation/test-report hygiene only; it does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## v27 Final Full-Test SUITESETTLE Lock

A final optional full-test runner pass found that, in constrained review environments, the `unittest` child can print its final `OK` summary but keep the interpreter process alive briefly afterward. `scripts/run_full_tests.py` now treats the file-backed unittest summary as a completion marker, waits a short settle period, and then cleans the child process group while preserving the printed pass/fail result. This is test-runner reliability work only; it does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

Latest validation in this dependency-light review environment:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks
- `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules, 20 skipped runtime-dependency tests
- `python scripts/check_release_zip.py` -> pass

Note: a runtime-dependency-installed environment may observe one additional runtime-oriented test, so the optional full-test count can be 154/155 depending on installed Flask/Socket.IO dependencies.
## v27 Final Full-Test DOCEXIT Lock

A final documentation-exit audit removed stale wording from the PROCESSRETURN snapshot that incorrectly described the current wrappers as returning through normal `SystemExit`. The active implementation and current documentation now agree: validation wrappers use bounded child-process groups, final `os.write()` payload output, and top-level `os._exit()` to avoid interpreter-shutdown waits after validation has completed. This is documentation accuracy only; it does not add packet capture, packet sending, network scanning, IDS, IPS, blocking, or production monitoring capability.

## v27 Final Full-Test DEPSCOUNT Lock

Synchronized the latest full-test documentation with the two expected reviewer environments: dependency-light runs can observe 154 tests with 20 runtime-dependency tests skipped, while runtime-dependency-installed runs observe 155 tests with no skips. This is documentation accuracy only; it does not add packet capture, packet sending, network scanning, IDS, IPS, blocking, or production monitoring capability.


## PIPEFREE Lock

The optional full-test sweep was hardened for constrained reviewer sandboxes by moving project-local script checks in the unittest suite away from `subprocess.run(capture_output=True)`. Those tests now use a shared `tests/process_helpers.py` helper that runs local Python script entrypoints in-process with captured stdout/stderr and keeps a file-backed process-group fallback for non-project commands.

Observed validation:

- `python scripts/validate_project.py` -> pass
- `python scripts/run_clean_validation.py` -> pass, 4/4 checks passed
- `python scripts/run_full_tests.py` -> pass, 154 tests observed across 21/21 discovered modules in dependency-light mode, 20 runtime-dependency tests skipped
- `python scripts/check_release_zip.py` -> pass, no errors or warnings

This lock changes test execution hygiene only. It does not add live IPv6 packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, blocking, or production monitoring capability.

## PIPEFREE Count Sync

After adding the pipe-free helper regression check, the dependency-light optional full-test run now observes 154 tests across 21/21 discovered modules with 20 runtime-dependency tests skipped. A runtime-dependency-installed reviewer environment is expected to observe 155 tests with the runtime tests active. This is test/report synchronization only and does not change the simulator capability boundary.


## PIPEFREE Count Span Sync

A final count-span audit corrected one stale historical note that still said the optional full-test count could be older 148-to-149. The current expected span is `154/155`: dependency-light reviewer environments observe 154 tests with runtime-dependent tests skipped, and runtime-dependency-installed environments observe 155 tests. This is documentation/test hygiene only and does not change the simulator capability boundary.

## v27 CDN fallback wording lock

A final active-document wording audit changed the remaining English CDN fallback notes from generic “blocked” language to “access restricted” language. This keeps active reviewer-facing docs aligned with the simulation-only claim tone. The optional full-test count is now expected to span `154/155`: dependency-light reviewer environments observe 154 tests with runtime-dependent tests skipped, and runtime-dependency-installed environments observe 155 tests. This is documentation/test hygiene only and does not change the simulator capability boundary.


## v27 Final Full-Test COUNTDOCNORMAL Lock

A final count-documentation audit corrected stale historical lines that paired `154 tests observed` with `20 skipped runtime-dependency tests` or described 154 tests as dependency-light mode. The current expected span is unchanged and now consistently documented: dependency-light reviewer environments observe 154 tests with 20 runtime-dependent tests skipped, while runtime-dependency-installed environments observe 155 tests with no skips. This is documentation/test hygiene only and does not change the simulator capability boundary.


### PROCESSHELPER_EXITGUARD Lock
A final test-helper hardening pass made `tests/process_helpers.py` refuse in-process execution for project scripts that intentionally call `os._exit()`. Those scripts now fall back to the file-backed subprocess path, preventing a future unittest from accidentally terminating the whole discovery process while preserving the pipe-free helper path for normal project-local check scripts. This is validation-runner hygiene only and does not change simulator behavior or add live network capability.


### PROCESSHELPER_EXITGUARD Count Sync
After adding the process-helper exit-guard regression test, the expected optional full-test span is now `154/155`: dependency-light reviewer environments observe 154 tests with 20 runtime-dependent tests skipped, and runtime-dependency-installed environments observe 155 tests with no skips. This is documentation/test-count hygiene only and does not change the simulator capability boundary.

## v27 DOCREVIEW Lock

- Removed stale reviewer-facing `python -m compileall -q .` commands from the active README and Makefile test path.
- The recommended quick handoff check remains `python scripts/run_clean_validation.py`; the optional deep sweep is `python scripts/run_full_tests.py`.
- This keeps reviewer-created `.venv` directories out of broad compile walks and aligns the docs with the pruned validation design.
- Normalized the Korean CDN fallback wording to describe CDN access as restricted rather than blocked.


After the DOCREVIEW regression tests, the runtime-dependency-installed full sweep observed 155 tests. Dependency-light reviewers are expected to observe 154 tests with runtime-dependent tests skipped.

## WINPATH Lock

- Normalized release artifact path comparisons to POSIX-style relative paths so Windows PowerShell reviewers get the same results as Unix-like environments.
- Kept the package simulation-only; no packet capture, packet sending, network scanning, or blocking capability was added.
- `python scripts/run_full_tests.py` -> pass after WINPATH guard, 154/155 expected tests depending on runtime dependency availability.

### Windows validation process-control hardening

A final Windows reviewer pass moved validation timeout cleanup into `services/process_control.py`. The validation wrappers now use a portable subprocess-isolation helper: POSIX keeps new-session process-group cleanup, while Windows uses `CREATE_NEW_PROCESS_GROUP` when available and falls back to terminate/kill cleanup on timeout. This is validation-runner reliability work only; it does not add live IPv6 packet capture, packet sending, network scanning, IDS, IPS, blocking, or production monitoring capability.

## v27 final Windows inventory ordering lock

A final Windows handoff fix made file-inventory and release-ZIP ordering explicitly platform-stable by sorting on normalized POSIX-style relative paths instead of OS-specific `Path` ordering. This prevents identical extracted source trees from producing different aggregate inventory digests on Windows versus Linux/macOS.

This is packaging/integrity hygiene only. It does not add packet capture, packet sending, network scanning, spoofing, MITM, IDS, IPS, or production monitoring capability.
