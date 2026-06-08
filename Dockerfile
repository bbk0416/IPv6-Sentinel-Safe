FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    IPV6_SENTINEL_HOST=127.0.0.1 \
    IPV6_SENTINEL_PORT=5000

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python scripts/smoke_check.py --url http://127.0.0.1:5000/api/ready

CMD ["python", "app.py"]
