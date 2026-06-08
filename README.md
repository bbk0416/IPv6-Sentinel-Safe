# IPv6 Sentinel Safe

**IPv6 Sentinel Safe**는 실제 네트워크를 스캔하거나 패킷을 송수신하지 않는 **안전한 로컬 IPv6 보안 이벤트 시뮬레이터**입니다.

포트폴리오, 교육, 시연을 위해 만든 프로젝트입니다. 실제 IDS/IPS, 패킷 분석기, 네트워크 스캐너, 차단 자동화 도구가 아닙니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 버전 | **27.0.0-safe / v27** |
| 패키지 버전 | `27.0.0` — normalized PEP 440 package version |
| 모드 | `safe_simulation` |
| 실행 방식 | 로컬 Flask + Socket.IO 대시보드 |
| 기본 주소 | `http://127.0.0.1:5000` |
| 현재 v27 대시보드 | 로컬 샘플 데이터 기반 시각화 |
| 검증 상태 | Windows PowerShell 기준 전체 검증 및 전체 테스트 통과 |
| 안전 범위 | 실제 패킷 캡처 없음, 실제 패킷 전송 없음, 실제 네트워크 스캔 없음 |

## 이 프로젝트의 목적

이 프로젝트는 “실제 공격/탐지 도구”가 아니라, **보안 이벤트 대응 흐름을 안전하게 보여주는 데모 환경**입니다.

주요 목표는 다음과 같습니다.

- IPv6 보안 이벤트를 로컬 샘플 데이터로 시각화
- 대시보드, API, 문서, 테스트, 릴리스 검증을 하나의 패키지로 구성
- public 포트폴리오에서 안전 범위와 한계를 명확히 제시
- Windows 환경에서도 동일하게 검증되는 제출용 프로젝트 구성

## 주요 기능

- IPv6 보안 이벤트 시나리오 시뮬레이션
- DHCPv6, DNS, Neighbor Discovery, Router Advertisement 관측 이벤트 데모
- Flask/Socket.IO 기반 실시간 대시보드
- Socket.IO 클라이언트가 없어도 동작하는 `REST fallback` 제어 경로
- CDN 접근이 제한되어도 로컬 REST 경로로 시연 가능
- 로컬 샘플 자산 생성 및 자산 상세 모달
- 관측 로그, 통계, 안전 점수 표시
- CSV 로그 내보내기 및 JSON 스냅샷 내보내기
- API 계약, 응답 스키마, 릴리스 품질 게이트 포함
- 파일 인벤토리 무결성 검증 포함
- Windows/macOS/Linux 실행 스크립트 포함
- Docker / Docker Compose 실행 지원

## 미리보기

대시보드 미리보기 파일은 아래 경로에 있습니다.

```txt
docs/assets/dashboard-preview.svg
docs/assets/dashboard-preview.png
```

## 빠른 실행

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

또는:

```powershell
.\run.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

또는:

```bash
chmod +x run.sh
./run.sh
```

실행 후 브라우저에서 아래 주소를 엽니다.

```txt
http://127.0.0.1:5000
```

## Docker 실행

Docker Compose는 외부 포트 노출을 전제로 하므로 기본 인증 비밀번호를 직접 지정해야 합니다. 현재 v27 패키지에서도 비밀번호를 직접 지정하지 않으면 실행이 실패합니다.

```bash
IPV6_SENTINEL_PASSWORD=change-me-local-demo docker compose up --build
```

직접 빌드하려면 아래 명령을 사용합니다.

```bash
docker build -t ipv6-sentinel-safe:latest .
docker run --rm -p 5000:5000 \
  -e IPV6_SENTINEL_HOST=0.0.0.0 \
  -e IPV6_SENTINEL_WEB_AUTH_ENABLED=1 \
  -e IPV6_SENTINEL_USERNAME=admin \
  -e IPV6_SENTINEL_PASSWORD='change-me-local-demo' \
  ipv6-sentinel-safe:latest
```

## v27 검증 기준

가장 먼저 아래 명령을 실행합니다.

```powershell
python scripts/run_clean_validation.py
```

의존성 파일만 따로 확인하려면 아래 명령을 사용합니다.

```powershell
python scripts/check_requirements.py
```

전체 단위 테스트까지 확인하려면 아래 명령을 추가로 실행합니다.

```powershell
python scripts/run_full_tests.py
```

Windows PowerShell 검증 기준은 다음과 같습니다.

```txt
file inventory: pass
clean validation: pass
project validation: pass
full unittest discovery: 158 tests passed
```

검증 위생 흐름은 `docs/quality/VALIDATION_HYGIENE.md`의 `validation_hygiene` 기준을 따릅니다.

릴리스 제출 전 전체 체크리스트를 보고 싶으면 아래 명령을 사용합니다.

```powershell
python scripts/final_handoff_check.py --plan
```

## 주요 API

| 경로 | 방식 | 설명 |
|---|---:|---|
| `/api/health` | GET | 앱 상태 확인 |
| `/api/ready` | GET | 실행 준비 상태 확인 |
| `/api/info` | GET | 안전 모드와 설정 메타데이터 조회 |
| `/api/diagnostics` | GET | 리뷰어용 진단 정보 확인 |
| `/api/preflight` | GET | 실행 전 상태 점검 |
| `/api/stats` | GET | 대시보드 통계 조회 |
| `/api/assets` | GET | 로컬 샘플 자산 목록 조회 |
| `/api/assets/generate` | POST | 로컬 샘플 자산 생성 |
| `/api/monitoring/start` | POST | 시뮬레이션 표시 시작 |
| `/api/monitoring/stop` | POST | 시뮬레이션 표시 중지 |
| `/api/logs` | GET | 최근 관측 로그 조회 |
| `/api/logs.csv` | GET | 관측 로그 CSV 다운로드 |
| `/api/snapshot.json` | GET | 통계·자산·로그·설정 스냅샷 다운로드 |
| `/api/report.json` | GET | 포트폴리오 검토용 안전성 리포트 다운로드 |
| `/api/settings` | GET/POST | 대시보드 설정 조회 및 저장 |
| `/api/demo/scenario` | POST | 데모 시나리오 생성 |
| `/api/quality` | GET | 품질 게이트 요약 확인 |
| `/api/contract` | GET | API 계약 정합성 확인 |
| `/api/schema` | GET | 응답 스키마 계약 확인 |
| `/api/release` | GET | 릴리스 식별자 확인 |
| `/api/artifact` | GET | 릴리스 산출물 위생 확인 |
| `/api/publication` | GET | 공개용 위생 검사 확인 |
| `/api/gates` | GET | 품질 게이트 목록 확인 |
| `/api/integrity` | GET | 파일 인벤토리 무결성 확인 |
| `/api/capabilities` | GET | 지원 범위와 비지원 범위 확인 |
| `/api/reviewer` | GET | 리뷰어용 요약 정보 확인 |

## 안전 설계 원칙

- 기본 바인딩은 `127.0.0.1`입니다.
- 원격 접근 가능한 주소로 열 때는 기본적으로 인증이 필요합니다.
- CORS 기본값은 localhost 명시 허용이며 와일드카드 `*`를 기본으로 사용하지 않습니다.
- 대시보드에 표시되는 자산과 이벤트는 모두 로컬 샘플 데이터입니다.
- 실제 네트워크 트래픽을 만들거나 보내는 의존성은 사용하지 않습니다.
- 로그와 사용자 설정은 로컬 `logs/`, `data/` 폴더에 저장됩니다.
- 검증 과정에서 생기는 캐시와 런타임 산출물은 릴리스 패키지에 포함하지 않습니다.

## 이 프로젝트가 하지 않는 것

| 항목 | 지원 여부 |
|---|---:|
| 실제 IPv6 패킷 캡처 | 미지원 |
| 실제 패킷 송신 | 미지원 |
| 실제 네트워크 스캔 | 미지원 |
| 실장비 탐색 | 미지원 |
| DHCP/DNS 변조 | 미지원 |
| IDS/IPS 운영 탐지 | 미지원 |
| 차단 자동화 | 미지원 |

## 포트폴리오 설명 문구

> IPv6 Sentinel Safe는 실제 네트워크를 스캔하거나 패킷을 송수신하지 않는 안전한 로컬 IPv6 보안 이벤트 시뮬레이터입니다. Flask/Socket.IO 기반 대시보드, IPv6 보안 이벤트 시나리오, API 계약, 파일 인벤토리 무결성 검증, 릴리스 품질 게이트, Windows 검증까지 포함한 포트폴리오용 보안 시뮬레이션 프로젝트입니다.

## 문서 구조

| 문서 | 설명 |
|---|---|
| `PORTFOLIO_SUMMARY.md` | 포트폴리오용 요약 |
| `PROJECT_COMPLETION_REPORT.md` | 완성 보고서 |
| `VALIDATION_REPORT.md` | 검증 결과 요약 |
| `RELEASE_NOTES_v27.md` | 현재 최종 릴리스 노트 |
| `docs/review/HONEST_LIMITATIONS.md` | 한계와 비기능 범위 |
| `docs/quality/CAPABILITY_BOUNDARY.md` | 지원 범위와 비지원 범위 |
| `docs/quality/VALIDATION_HYGIENE.md` | validation_hygiene 검증 흐름 |
| `docs/release/FILE_INVENTORY.json` | 파일 인벤토리 무결성 기준 |

## 제출 시 요약

```txt
Safe local IPv6 security-event simulator.
No packet capture, no packet sending, no network scanning.
Windows-verified validation and 158-test discovery pass.
```

## 라이선스

이 프로젝트는 `LICENSE` 파일의 조건을 따릅니다.
