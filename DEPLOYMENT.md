# Deployment Guide

## 1. 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

접속 주소:

```text
http://127.0.0.1:5000
```

## 2. Docker 실행

```bash
docker build -t ipv6-sentinel-safe:latest .
docker run --rm -p 5000:5000 \
  -e IPV6_SENTINEL_HOST=0.0.0.0 \
  -e IPV6_SENTINEL_WEB_AUTH_ENABLED=1 \
  -e IPV6_SENTINEL_USERNAME=admin \
  -e IPV6_SENTINEL_PASSWORD='change-me-local-demo' \
  ipv6-sentinel-safe:latest
```

브라우저에서 `http://127.0.0.1:5000` 접속 후 Basic Auth 계정을 입력합니다.

## 3. Docker Compose 실행

```bash
IPV6_SENTINEL_PASSWORD=change-me-local-demo docker compose up --build
```

`docker-compose.yml`은 외부 포트를 열기 때문에 Basic Auth를 기본 활성화합니다. 실제 사용 전 `IPV6_SENTINEL_PASSWORD` 값을 반드시 바꾸세요.

## 4. 준비 상태 확인

```bash
python scripts/smoke_check.py --url http://127.0.0.1:5000/api/ready
```

정상일 때:

```text
ready
```

## 5. 배포 전 점검

```bash
python scripts/run_clean_validation.py
```

이 명령은 clean validation wrapper를 통해 다음을 확인합니다.

- Python 문법 컴파일
- 단위 테스트
- 위험 의존성 import 여부
- 필수 문서/배포 파일 존재 여부
