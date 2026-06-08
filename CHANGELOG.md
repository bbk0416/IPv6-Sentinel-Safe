# Changelog

## 4.0.0-safe

- Dockerfile, docker-compose.yml, .dockerignore 추가
- GitHub Actions CI 추가
- pyproject.toml, Makefile 추가
- `/api/ready` 준비 상태 API 추가
- smoke check / release validation scripts 추가
- 포트폴리오 요약 문서와 배포 가이드 추가
- 정적 대시보드 preview SVG 추가


## 3.2.0-safe

- Added safe-mode metadata endpoint `/api/info`.
- Added dashboard snapshot export `/api/snapshot.json`.
- Added security headers and fail-closed remote bind guard.
- Hardened `.env` parsing and Basic Auth comparison.
- Added runtime tests for auth, snapshot export, and remote-bind safety.
- Added `SECURITY_CHECKLIST.md` and v3 release notes.


## 3.1.0-safe

- Hardened `psutil` handling so missing network counters do not crash startup.
- Added runtime Flask route tests.
- Added `/api/reset` for local simulation reset.
- Added `/api/logs.csv` for safe log export.
- Cleaned legacy environment-variable fallbacks and old branding remnants.
- Fixed dashboard HTML structure and added reset/export controls.

## 3.0.0-safe

- Converted the project into a safe IPv6 monitoring simulator.
- Removed live packet capture, packet transmission, and real network scan behavior.
- Added local sample assets, observations, dashboard settings, and static safety tests.
