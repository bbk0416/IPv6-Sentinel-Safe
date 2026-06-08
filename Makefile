PYTHON ?= python

.PHONY: setup run test validate full-test project-validate clean-validate contract schema-contract release-identity release-artifact file-inventory manifest-hygiene validation-hygiene publication-hygiene gate-registry capability-boundary reviewer-handoff final-handoff release-zip ci-check clean build-release docker-build docker-run release-matrix check-route-hygiene check-manifest-hygiene

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements.txt

run:
	$(PYTHON) app.py

test:
	$(PYTHON) scripts/run_clean_validation.py
	$(PYTHON) scripts/run_full_tests.py

validate:
	$(PYTHON) scripts/run_clean_validation.py

full-test:
	$(PYTHON) scripts/run_full_tests.py

project-validate:
	$(PYTHON) scripts/validate_project.py

clean-validate:
	$(PYTHON) scripts/run_clean_validation.py

contract:
	$(PYTHON) scripts/check_api_contract.py

schema-contract:
	$(PYTHON) scripts/check_schema_contract.py

release-identity:
	$(PYTHON) scripts/check_release_identity.py

release-artifact:
	$(PYTHON) scripts/check_release_artifact.py

file-inventory:
	$(PYTHON) scripts/check_file_inventory.py

manifest-hygiene:
	$(PYTHON) scripts/check_manifest_hygiene.py

validation-hygiene:
	$(PYTHON) scripts/check_validation_hygiene.py

publication-hygiene:
	$(PYTHON) scripts/check_publication_hygiene.py

gate-registry:
	$(PYTHON) scripts/check_gate_registry.py

capability-boundary:
	$(PYTHON) scripts/check_capability_boundary.py

reviewer-handoff:
	$(PYTHON) scripts/check_reviewer_handoff.py

final-handoff:
	$(PYTHON) scripts/final_handoff_check.py

release-zip:
	$(PYTHON) scripts/check_release_zip.py

ci-check:
	$(PYTHON) scripts/check_ci_workflow.py

clean:
	$(PYTHON) scripts/clean_release_artifacts.py

build-release:
	$(PYTHON) scripts/build_release.py --output ../IPv6Sentinel_SAFE_v27_release.zip

docker-build:
	docker build -t ipv6-sentinel-safe:latest .

docker-run:
	docker compose up --build

release-matrix:
	$(PYTHON) scripts/check_release_matrix.py
	$(PYTHON) scripts/check_route_hygiene.py
	$(PYTHON) scripts/check_manifest_hygiene.py
	$(PYTHON) scripts/check_validation_hygiene.py
	$(PYTHON) scripts/check_publication_hygiene.py
	$(PYTHON) scripts/check_gate_registry.py
	$(PYTHON) scripts/check_capability_boundary.py
	$(PYTHON) scripts/check_reviewer_handoff.py

check-route-hygiene:
	$(PYTHON) scripts/check_route_hygiene.py

check-manifest-hygiene:
	$(PYTHON) scripts/check_manifest_hygiene.py

