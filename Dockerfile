FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    IPV6_SENTINEL_HOST=127.0.0.1 \
    IPV6_SENTINEL_PORT=5000 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

RUN groupadd --gid 10001 ipv6sentinel \
    && useradd --uid 10001 --gid 10001 --no-log-init --create-home ipv6sentinel \
    && chown ipv6sentinel:ipv6sentinel /app

COPY --chown=ipv6sentinel:ipv6sentinel . .

USER ipv6sentinel

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python scripts/smoke_check.py --url http://127.0.0.1:5000/api/ready

CMD ["python", "app.py"]
