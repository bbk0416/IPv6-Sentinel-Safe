#!/usr/bin/env python3
"""Tiny dependency-free HTTP smoke check used by Docker HEALTHCHECK and CI."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/ready")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    try:
        with urllib.request.urlopen(args.url, timeout=args.timeout) as response:  # noqa: S310 - local health check URL
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
