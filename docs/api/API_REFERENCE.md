# API Reference

IPv6 Sentinel Safe의 API는 모두 로컬 시뮬레이션 데이터를 조회하거나 저장합니다. 실제 네트워크 스캔, 패킷 캡처, 패킷 전송 기능은 제공하지 않습니다.

## Health & readiness

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/health` | 앱이 살아 있는지 확인합니다. |
| GET | `/api/ready` | 안전 모드, 시뮬레이션 모드, 원격 바인딩 보호 상태를 점검합니다. |
| GET | `/api/info` | 앱 이름, 버전, 안전 플래그, 바인딩 정보를 반환합니다. |
| GET | `/api/integrity` | 릴리스 파일 인벤토리와 현재 소스 트리 해시가 일치하는지 확인합니다. |
| GET | `/api/manifest` | manifest의 release note, 문서, API 경로, reviewer export 일치성을 확인합니다. |
| GET | `/api/publication` | 공개/제출용 패키지에 개인 식별자, 사설 IP, 사용자 경로, 흔한 토큰 패턴이 섞였는지 확인합니다. |
| GET | `/api/gates` | 품질 게이트의 스크립트, 문서, 선택적 API 엔드포인트, manifest 등록 상태가 서로 맞는지 확인합니다. |
| GET | `/api/capabilities` | 지원 기능과 명시적 비기능 범위를 확인해 시뮬레이터 과장을 방지합니다. |
| GET | `/api/reviewer` | 검토자가 처음 볼 실행 순서, 안전한 주장, 금지 주장, 검토용 엔드포인트를 한 번에 확인합니다. |

## Dashboard data

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/stats` | 총 이벤트, DHCPv6/DNS 관측 수, 안전 점수 등 현재 통계를 반환합니다. |
| GET | `/api/assets` | 로컬 샘플 자산 목록을 반환합니다. |
| GET | `/api/assets/{asset_id}` | 특정 샘플 자산 상세 정보를 반환합니다. |
| GET | `/api/performance` | CPU, 메모리, 네트워크 카운터 기반 표시용 성능 스냅샷을 반환합니다. |
| GET | `/api/logs` | 최근 관측 로그를 JSON으로 반환합니다. |
| GET | `/api/logs.csv` | 최근 관측 로그를 CSV 파일로 다운로드합니다. |
| GET | `/api/snapshot.json` | 통계, 자산, 로그, 설정을 하나의 JSON 파일로 다운로드합니다. |
| GET | `/api/report.json` | 포트폴리오 검토용 안전성/시연 요약 리포트를 다운로드합니다. |

## Local simulation controls

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/demo/scenario` | 포트폴리오 발표용 데모 데이터를 즉시 생성합니다. |
| POST | `/api/monitoring/start` | Socket.IO CDN이 없어도 REST 방식으로 로컬 시뮬레이션을 시작합니다. |
| POST | `/api/monitoring/stop` | REST 방식으로 로컬 시뮬레이션을 중지합니다. |
| POST | `/api/assets/generate` | REST 방식으로 샘플 자산 목록을 생성합니다. |
| POST | `/api/logs/clear` | REST 방식으로 로컬 로그를 초기화합니다. |
| POST | `/api/simulation/speed` | REST 방식으로 시뮬레이션 속도를 1~10 사이로 저장합니다. |
| POST | `/api/reset` | 로컬 시뮬레이션 데이터와 카운터를 초기화합니다. |
| GET/POST | `/api/settings` | 대시보드 설정을 조회하거나 저장합니다. |

## Example

```bash
curl http://127.0.0.1:5000/api/info
curl -X POST http://127.0.0.1:5000/api/demo/scenario
curl -X POST http://127.0.0.1:5000/api/assets/generate
curl -X POST http://127.0.0.1:5000/api/monitoring/start
curl -O http://127.0.0.1:5000/api/snapshot.json
```

## Security note

- 기본 실행 주소는 `127.0.0.1`입니다.
- `0.0.0.0`로 열 때는 Basic Auth를 켜야 합니다.
- API는 실장비에 영향을 주는 명령을 수행하지 않습니다.


## GET `/api/report.json`

Reviewer-friendly JSON export containing project metadata, safety checks, demo summary, and limitations.
Use this when you want to submit a compact proof that the project is simulation-only.


## REST fallback

대시보드는 Socket.IO 클라이언트 CDN을 불러오지 못해도 `/api/monitoring/start`, `/api/assets/generate`, `/api/logs/clear`, `/api/simulation/speed` 엔드포인트로 기본 시연 흐름을 유지합니다. 이 기능도 모두 로컬 샘플 데이터에만 작동합니다.

## GET /api/diagnostics

Returns runtime/static safety diagnostics for reviewers.

Example response fields:

- `status`: `pass` or `fail`
- `version`: app version
- `mode`: `safe_simulation`
- `checks`: list of diagnostic checks

This endpoint only reviews app flags and source-level safety indicators. It does not scan, capture, or transmit network traffic.


## GET /api/preflight

Runs read-only local preflight checks for portfolio review and demo operation.
It verifies Python/runtime dependency availability, safe-mode flags, disabled real packet features, CORS safety, bind/auth posture, and required review documents.

Response status is `200` when all blocking checks pass and `503` when a blocking check fails.

## GET /api/quality

Runs read-only release quality checks for reviewers.
It verifies version consistency, required documentation, excluded runtime artifacts, simulation-only manifest flags, and absence of blocked runtime imports.

Response status is `200` when the release quality gate passes and `503` when a blocking check fails.

This endpoint proves package/review consistency only. It does not prove real network detection capability.

### Preflight profile note

The `/api/preflight` endpoint represents runtime validation. For source-package review before installing dependencies, use `python scripts/preflight_check.py`; it reports missing runtime modules as warnings. Use `python scripts/preflight_check.py --strict` after dependency installation.


## GET /api/contract

Runs a read-only API contract check. It compares Flask route declarations, `docs/api/openapi.yaml`, `docs/api/API_REFERENCE.md`, and `project_manifest.json` so reviewers can spot stale documentation before treating the package as release-ready.

This endpoint does not start scans, capture packets, send packets, or contact external services.


## GET /api/schema

Returns the v27 reviewer-facing data contract for local simulator payloads. It documents the expected shapes for `stats`, `asset`, `log`, and `settings` objects so API consumers and reviewers can verify that exported data is not just undocumented ad-hoc JSON.

This endpoint is documentation/validation support only. It does not scan, capture, send packets, or claim real detection coverage.


## GET /api/release

Runs a read-only release identity check. It verifies that the safe release ID is aligned across source settings, OpenAPI, `project_manifest.json`, README, validation reports, and release handoff files, while `pyproject.toml` uses the normalized PEP 440 package version.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks release-ID and normalized package-version consistency.

## GET /api/artifact

Runs a read-only release artifact hygiene check. It verifies that required handoff files exist, runtime/cache artifacts are not packaged, run scripts are present, the current release note is declared once, and the manifest still declares the project as safe simulation only.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks package hygiene for review and release handoff.


## GET /api/integrity

Runs a read-only file inventory integrity check. It compares the current clean source tree against `docs/release/FILE_INVENTORY.json`, including per-file SHA-256 hashes and an aggregate package digest.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks release package integrity for review and handoff.


## GET /api/manifest

Runs a read-only manifest hygiene check. It verifies that `project_manifest.json` has no duplicate list entries, declares all release note files, points only to existing final documents, keeps reviewer exports aligned with API endpoints, and still states the simulation-only boundary.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks reviewer metadata consistency.


## GET /api/publication

Runs a read-only publication hygiene check. It verifies that the handoff package does not include obvious personal identifiers, plain email addresses, private IPv4 addresses, user home paths, legacy project names, common credential patterns, or stale current-version markers in older release notes.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks public-release cleanliness for review and handoff.


## GET /api/gates

Runs a read-only central quality-gate registry check. It verifies that reviewer-facing gates have matching scripts, documentation, manifest entries, and optional API endpoints. This keeps the growing validation suite maintainable and easier to review.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only checks release-maintenance metadata for the safe simulator package.


## GET /api/capabilities

Runs a read-only capability boundary check. It returns the simulator-supported capabilities, explicit non-capabilities, and validation checks that confirm the package is not claiming live IPv6 IDS, scanner, sniffer, packet sender, spoofing, MITM, or exploit behavior.

This endpoint does not scan, capture, transmit, or claim real IPv6 detection. It only documents and validates the safe simulator scope.


## GET /api/reviewer

Returns a read-only reviewer handoff summary. It lists first-run commands, safe portfolio claims, explicit non-claims, and review entry points. It is intended to prevent overclaiming: the project remains a local educational simulator and not a live IPv6 network security product.
