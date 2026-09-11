# Deployment Guide

## 1. 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

접속 주소:

```text
http://127.0.0.1:5000
```

기본 실행은 로컬 전용입니다. 외부 네트워크에서 직접 접근시키지 않는 것이 기본 운영 방식입니다.

## 2. Docker 로컬 실행

Docker 컨테이너 내부에서는 앱이 `0.0.0.0:5000`을 사용하지만, 호스트에는 loopback으로만 포트를 공개합니다. 컨테이너는 Flask 개발 서버가 아니라 Gunicorn 단일 worker + threaded WebSocket 구성을 사용합니다. 로컬 `python app.py` 실행은 계속 localhost 전용 embedded server 경로입니다.

```bash
docker build -t ipv6-sentinel-safe:latest .
docker run --rm -p 127.0.0.1:5000:5000 \
  -e IPV6_SENTINEL_HOST=0.0.0.0 \
  -e IPV6_SENTINEL_WEB_AUTH_ENABLED=1 \
  -e IPV6_SENTINEL_USERNAME=admin \
  -e IPV6_SENTINEL_PASSWORD='change-me-local-demo' \
  ipv6-sentinel-safe:latest
```

브라우저에서 `http://127.0.0.1:5000`에 접속해 Basic Auth 계정을 입력합니다.

## 3. Docker Compose 로컬 실행

```bash
IPV6_SENTINEL_PASSWORD=change-me-local-demo docker compose up --build
```

`docker-compose.yml`의 기본 publish 주소는 `127.0.0.1:5000`입니다. 따라서 같은 호스트가 아닌 다른 장치에서는 5000번 포트로 직접 접속할 수 없습니다. Basic Auth는 계속 활성화되며 비밀번호도 반드시 지정해야 합니다.

## 4. 원격 접속: HTTPS reverse proxy 사용

**Basic Auth는 자격증명을 암호화하지 않습니다.** 원격 접속에 평문 HTTP를 사용하면 자격증명이 노출될 수 있으므로, 5000번 포트를 외부에 직접 공개하지 말고 같은 호스트의 HTTPS reverse proxy를 앞에 둡니다.

아래 예시는 공개 주소를 `https://sentinel.example.com`으로 가정합니다. 실제 도메인으로 바꾸세요.

먼저 앱의 허용 Origin을 공개 HTTPS 주소와 정확히 맞춥니다.

```bash
export IPV6_SENTINEL_PASSWORD='replace-with-a-strong-password'
export IPV6_SENTINEL_CORS='https://sentinel.example.com'
docker compose up -d --build
```

`IPV6_SENTINEL_CORS`는 Socket.IO CORS와 인증된 상태 변경 REST 요청의 Origin 검사에 함께 사용됩니다. `*` 대신 실제 공개 Origin을 지정합니다.

Nginx 예시:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name sentinel.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name sentinel.example.com;

    ssl_certificate     /etc/letsencrypt/live/sentinel.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sentinel.example.com/privkey.pem;

    client_max_body_size 64k;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 75s;
    }
}
```

인증서와 개인키는 저장소에 넣지 않습니다. 운영 호스트의 인증서 관리 도구나 별도 비밀 저장소에서 관리합니다.

방화벽에서는 외부에서 필요한 80/443만 허용하고 **5000/tcp는 외부에 열지 않습니다**. 실제 원격 사용에서 `IPV6_SENTINEL_ALLOW_INSECURE_REMOTE=1`로 우회하지 않습니다.

Nginx와 앱이 같은 호스트에 있으므로 proxy upstream은 `127.0.0.1:5000`을 사용합니다. 앱은 전달된 `X-Forwarded-*` 헤더를 신뢰해 보안 결정을 완화하지 않으며, 공개 브라우저 Origin은 위의 `IPV6_SENTINEL_CORS` 값으로 명시합니다.

## 5. 준비 상태 확인

로컬 upstream 확인:

```bash
IPV6_SENTINEL_WEB_AUTH_ENABLED=1 \
IPV6_SENTINEL_USERNAME=admin \
IPV6_SENTINEL_PASSWORD='replace-with-a-strong-password' \
python scripts/smoke_check.py --url http://127.0.0.1:5000/api/ready
```

정상일 때:

```text
ready
```

HTTPS 공개 주소는 브라우저에서 인증서 오류가 없는지 먼저 확인합니다. CLI로 확인할 때는 비밀번호를 명령행 인자에 직접 넣지 말고 프롬프트나 안전한 비밀 주입 방식을 사용합니다.

## 6. 배포 전 점검

```bash
python scripts/run_clean_validation.py
python scripts/run_full_tests.py
```

이 검증은 다음을 확인합니다.

- Python 문법과 프로젝트 품질 게이트
- 전체 단위 테스트
- 위험 의존성 import 여부
- 필수 문서/배포 파일 존재 여부
- 파일 인벤토리 무결성

## 7. 원격 배포 체크리스트

- 앱/컨테이너의 5000번 포트는 `127.0.0.1`에만 publish
- 외부 진입점은 HTTPS 443
- HTTP 80은 HTTPS로 리다이렉트
- `IPV6_SENTINEL_WEB_AUTH_ENABLED=1`
- 강한 `IPV6_SENTINEL_PASSWORD` 사용
- `IPV6_SENTINEL_CORS=https://실제-도메인`으로 정확히 지정
- TLS 개인키와 비밀번호를 Git에 커밋하지 않음
- `IPV6_SENTINEL_ALLOW_INSECURE_REMOTE=1`을 실제 원격 배포에 사용하지 않음
