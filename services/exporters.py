"""Safe export helpers for logs and JSON snapshots."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Iterable, Mapping

from flask import Response

LOG_CSV_FIELDS = ["timestamp", "event_type", "asset", "status", "message"]


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def json_attachment(payload: Mapping[str, Any], filename_prefix: str) -> Response:
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    filename = f"{filename_prefix}-{timestamp_slug()}.json"
    return Response(
        body,
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def logs_csv_attachment(logs: Iterable[Mapping[str, Any]]) -> Response:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=LOG_CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for entry in logs:
        writer.writerow({key: entry.get(key, "") for key in LOG_CSV_FIELDS})
    return Response(
        buffer.getvalue(),
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=ipv6_sentinel_logs.csv"},
    )
