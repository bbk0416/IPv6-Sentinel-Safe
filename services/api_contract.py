"""Read-only API contract consistency checks.

This module compares the Flask route declarations, OpenAPI document, API
reference, and project manifest. It is intentionally static: it reads local
files only and never starts the server, opens sockets, scans networks, or sends
packets.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


@dataclass(frozen=True, order=True)
class ApiRoute:
    path: str
    method: str

    def to_dict(self) -> dict[str, str]:
        return {"method": self.method, "path": self.path}


def _normalize_flask_path(path: str) -> str:
    """Convert Flask path converters to OpenAPI-style placeholders."""

    def replace(match: re.Match[str]) -> str:
        content = match.group(1)
        name = content.split(":", 1)[-1]
        return "{" + name + "}"

    return re.sub(r"<([^>]+)>", replace, path)


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _methods_from_route_decorator(call: ast.Call) -> set[str]:
    for keyword in call.keywords:
        if keyword.arg != "methods":
            continue
        value = keyword.value
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            methods = {
                str(item.value).upper()
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
            return methods or {"GET"}
    return {"GET"}


def extract_flask_api_routes(app_source: str) -> set[ApiRoute]:
    """Extract /api route/method pairs from Flask route decorators."""
    tree = ast.parse(app_source)
    routes: set[ApiRoute] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute) or func.attr != "route":
                continue
            if not decorator.args:
                continue
            path = _literal_string(decorator.args[0])
            if not path or not path.startswith("/api/"):
                continue
            normalized = _normalize_flask_path(path)
            for method in _methods_from_route_decorator(decorator):
                if method in HTTP_METHODS:
                    routes.add(ApiRoute(normalized, method))
    return routes


def extract_openapi_routes(openapi_text: str) -> set[ApiRoute]:
    """Extract /api route/method pairs from a simple OpenAPI YAML document.

    The project intentionally avoids a YAML dependency, so this parser only
    handles the path/method structure used by docs/api/openapi.yaml.
    """
    routes: set[ApiRoute] = set()
    current_path: str | None = None
    in_paths = False
    path_pattern = re.compile(r"^  (/api/[^:]+):\s*$")
    method_pattern = re.compile(r"^    (get|post|put|patch|delete):\s*$", re.IGNORECASE)

    for line in openapi_text.splitlines():
        if line.strip() == "paths:":
            in_paths = True
            current_path = None
            continue
        if not in_paths:
            continue
        if line and not line.startswith(" "):
            break
        path_match = path_pattern.match(line)
        if path_match:
            current_path = path_match.group(1)
            continue
        method_match = method_pattern.match(line)
        if method_match and current_path:
            routes.add(ApiRoute(current_path, method_match.group(1).upper()))
    return routes


def extract_manifest_paths(manifest_text: str) -> set[str]:
    try:
        payload = json.loads(manifest_text)
    except json.JSONDecodeError:
        return set()
    return {str(path) for path in payload.get("api_endpoints", []) if str(path).startswith("/api/")}


def _route_list(routes: Iterable[ApiRoute]) -> list[dict[str, str]]:
    return [route.to_dict() for route in sorted(routes)]


def run_api_contract_check(*, app_root: Path) -> dict[str, Any]:
    """Compare API declarations across source and docs."""
    app_text = (app_root / "app.py").read_text(encoding="utf-8", errors="ignore")
    openapi_text = (app_root / "docs" / "api" / "openapi.yaml").read_text(encoding="utf-8", errors="ignore")
    api_reference = (app_root / "docs" / "api" / "API_REFERENCE.md").read_text(encoding="utf-8", errors="ignore")
    manifest_text = (app_root / "project_manifest.json").read_text(encoding="utf-8", errors="ignore")

    flask_routes = extract_flask_api_routes(app_text)
    openapi_routes = extract_openapi_routes(openapi_text)
    manifest_paths = extract_manifest_paths(manifest_text)

    flask_paths = {route.path for route in flask_routes}
    openapi_paths = {route.path for route in openapi_routes}

    checks = [
        {
            "name": "flask_routes_documented_in_openapi",
            "ok": flask_routes == openapi_routes,
            "detail": {
                "missing_from_openapi": _route_list(flask_routes - openapi_routes),
                "extra_in_openapi": _route_list(openapi_routes - flask_routes),
            },
        },
        {
            "name": "manifest_api_paths_match_flask_routes",
            "ok": manifest_paths == flask_paths,
            "detail": {
                "missing_from_manifest": sorted(flask_paths - manifest_paths),
                "extra_in_manifest": sorted(manifest_paths - flask_paths),
            },
        },
        {
            "name": "api_reference_mentions_all_flask_paths",
            "ok": all(path in api_reference for path in sorted(flask_paths)),
            "detail": {
                "missing_from_api_reference": [path for path in sorted(flask_paths) if path not in api_reference],
            },
        },
    ]
    failures = [check for check in checks if not check["ok"]]
    return {
        "status": "pass" if not failures else "fail",
        "summary": {
            "flask_route_count": len(flask_routes),
            "openapi_route_count": len(openapi_routes),
            "manifest_path_count": len(manifest_paths),
            "failures": len(failures),
        },
        "checks": checks,
        "routes": _route_list(flask_routes),
    }
