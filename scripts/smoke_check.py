#!/usr/bin/env python3
"""Tiny dependency-free HTTP smoke check used by Docker HEALTHCHECK and CI."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from collections.abc import Mapping


def build_request(url: str, environ: Mapping[str, str] | None = None) -> urllib.request.Request:
    """Build the health-check request, adding Basic Auth when web auth is enabled."""
    env = os.environ if environ is None else environ
    request = urllib.request.Request(url)  # noqa: S310 - local health check URL
    auth_enabled = env.get("IPV6_SENTINEL_WEB_AUTH_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
    if not auth_enabled:
        return request

    username = env.get("IPV6_SENTINEL_USERNAME", "admin")
    password = env.get("IPV6_SENTINEL_PASSWORD", "")
    if not password:
        raise RuntimeError("IPV6_SENTINEL_PASSWORD is required when web auth is enabled")

    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {token}")
    return request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/ready")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    try:
        health_request = build_request(args.url)
        with urllib.request.urlopen(health_request, timeout=args.timeout) as response:  # noqa: S310 - local health check URL
            body = response.read().decode("utf-8")
            payload = json.loads(body)
            if response.status != 200 or payload.get("status") != "ready":
                print(f"not ready: status={response.status} payload={payload}", file=sys.stderr)
                return 1
    except Exception as exc:  # pragma: no cover - command-line utility
        print(f"smoke check failed: {exc}", file=sys.stderr)
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
