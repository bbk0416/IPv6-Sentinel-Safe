# Release Notes v4.0.0-safe

## 목표

v4는 IPv6 Sentinel Safe를 공개 저장소/포트폴리오 제출에 더 적합한 형태로 다듬은 릴리스입니다. 실제 네트워크 조작 기능은 계속 포함하지 않으며, 로컬 샘플 데이터 기반의 안전한 교육용 시뮬레이터 방향을 유지합니다.

## 추가 사항

- Dockerfile 추가
- docker-compose.yml 추가
- .dockerignore 추가
- pyproject.toml 추가
- Makefile 추가
- GitHub Actions CI 워크플로 추가
- `/api/ready` 준비 상태 점검 API 추가
- `scripts/smoke_check.py` 추가
- `scripts/validate_project.py` 추가
- 정적 대시보드 미리보기 SVG 추가
- 패키징/CI/도커 관련 정적 테스트 추가

## 검증 기준

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
python scripts/validate_project.py
```

의존성이 설치된 환경에서는 아래도 확인할 수 있습니다.

```bash
python app.py
python scripts/smoke_check.py --url http://127.0.0.1:5000/api/ready
```

## 안전성 유지 사항

- Scapy/mitmproxy/WMI 의존성 없음
- 실제 패킷 캡처/전송/네트워크 스캔 비활성화
- 기본 로컬 바인딩 유지
- Docker Compose로 외부 포트를 열 때 Basic Auth 기본 활성화
- CI에서 위험 의존성 import를 정적 검사
