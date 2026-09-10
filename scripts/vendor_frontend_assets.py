from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = ROOT / "static" / "vendor"
MANIFEST_PATH = VENDOR_ROOT / "VENDOR_MANIFEST.json"

PINNED_ASSETS = [
    {
        "name": "bootstrap-css",
        "version": "5.1.3",
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
        "path": "bootstrap/5.1.3/bootstrap.min.css",
        "integrity": "sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
    },
    {
        "name": "bootstrap-js",
        "version": "5.1.3",
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
        "path": "bootstrap/5.1.3/bootstrap.bundle.min.js",
        "integrity": "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
    },
    {
        "name": "socket.io-client",
        "version": "4.7.5",
        "url": "https://cdn.socket.io/4.7.5/socket.io.min.js",
        "path": "socket.io/4.7.5/socket.io.min.js",
        "integrity": "sha384-2huaZvOR9iDzHqslqwpR87isEmrfxqyWOF7hr7BY6KG0+hVKLoEXMPUJw3ynWuhO",
    },
    {
        "name": "chart.js",
        "version": "4.5.1",
        "url": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js",
        "path": "chart.js/4.5.1/chart.umd.min.js",
        "integrity": "sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ",
    },
    {
        "name": "font-awesome-css",
        "version": "6.0.0",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "path": "font-awesome/6.0.0/css/all.min.css",
        "integrity": "sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==",
    },
]

LICENSES = [
    {
        "name": "bootstrap",
        "version": "5.1.3",
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/LICENSE",
        "path": "licenses/bootstrap-5.1.3-LICENSE.txt",
    },
    {
        "name": "socket.io-client",
        "version": "4.7.5",
        "url": "https://cdn.jsdelivr.net/npm/socket.io-client@4.7.5/LICENSE",
        "path": "licenses/socket.io-client-4.7.5-LICENSE.txt",
    },
    {
        "name": "chart.js",
        "version": "4.5.1",
        "url": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/LICENSE.md",
        "path": "licenses/chart.js-4.5.1-LICENSE.md",
    },
    {
        "name": "font-awesome-free",
        "version": "6.0.0",
        "url": "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.0.0/LICENSE.txt",
        "path": "licenses/font-awesome-free-6.0.0-LICENSE.txt",
    },
]

THIRD_PARTY_NOTICE = """# Vendored frontend dependencies\n\nThese files are stored locally so the IPv6 Sentinel Safe dashboard does not need a third-party CDN at runtime.\n\n- Bootstrap 5.1.3 — MIT License\n- Socket.IO client 4.7.5 — MIT License\n- Chart.js 4.5.1 — MIT License\n- Font Awesome Free 6.0.0 — icons: CC BY 4.0; fonts: SIL OFL 1.1; code: MIT License\n\nExact source URLs and SHA-256 digests are recorded in `VENDOR_MANIFEST.json`. License texts are stored in the `licenses/` directory.\n\nDo not edit minified vendor files by hand. Refresh them with `python scripts/vendor_frontend_assets.py --write` and review the resulting manifest diff.\n"""


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "IPv6-Sentinel-Safe-vendor-refresh/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _verify_sri(data: bytes, integrity: str) -> None:
    algorithm, expected = integrity.split("-", 1)
    if algorithm not in {"sha384", "sha512"}:
        raise ValueError(f"Unsupported SRI algorithm: {algorithm}")
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode("ascii")
    if actual != expected:
        raise RuntimeError(f"SRI mismatch for {algorithm}: expected {expected}, got {actual}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_bytes(relative_path: str, data: bytes) -> dict[str, object]:
    target = VENDOR_ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {
        "path": relative_path,
        "size": len(data),
        "sha256": _sha256(data),
    }


def _font_urls(font_css: bytes, css_url: str) -> list[tuple[str, str]]:
    text = font_css.decode("utf-8")
    paths = sorted(set(re.findall(r"url\((?:['\"])?(\.\./webfonts/[^)'\"]+)(?:['\"])?\)", text)))
    return [(path.split("/")[-1], urljoin(css_url, path)) for path in paths]


def write_vendor_assets() -> None:
    if VENDOR_ROOT.exists():
        shutil.rmtree(VENDOR_ROOT)
    VENDOR_ROOT.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    font_css: bytes | None = None
    font_css_url = ""

    for asset in PINNED_ASSETS:
        data = _download(str(asset["url"]))
        _verify_sri(data, str(asset["integrity"]))
        record = _write_bytes(str(asset["path"]), data)
        record.update(
            {
                "name": asset["name"],
                "version": asset["version"],
                "source_url": asset["url"],
                "integrity": asset["integrity"],
            }
        )
        records.append(record)
        if asset["name"] == "font-awesome-css":
            font_css = data
            font_css_url = str(asset["url"])

    if font_css is None:
        raise RuntimeError("Font Awesome CSS was not downloaded")

    for filename, url in _font_urls(font_css, font_css_url):
        data = _download(url)
        relative = f"font-awesome/6.0.0/webfonts/{filename}"
        record = _write_bytes(relative, data)
        record.update(
            {
                "name": f"font-awesome-webfont-{filename}",
                "version": "6.0.0",
                "source_url": url,
                "integrity": None,
            }
        )
        records.append(record)

    for license_item in LICENSES:
        data = _download(str(license_item["url"]))
        record = _write_bytes(str(license_item["path"]), data)
        record.update(
            {
                "name": f"license-{license_item['name']}",
                "version": license_item["version"],
                "source_url": license_item["url"],
                "integrity": None,
            }
        )
        records.append(record)

    notice_bytes = THIRD_PARTY_NOTICE.encode("utf-8")
    notice_record = _write_bytes("THIRD_PARTY_NOTICES.md", notice_bytes)
    notice_record.update(
        {
            "name": "third-party-notices",
            "version": None,
            "source_url": None,
            "integrity": None,
        }
    )
    records.append(notice_record)

    manifest = {
        "schema_version": 1,
        "purpose": "Pinned frontend assets vendored for offline/local dashboard runtime",
        "generated_by": "scripts/vendor_frontend_assets.py",
        "assets": sorted(records, key=lambda item: str(item["path"])),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Vendored {len(records)} files into {VENDOR_ROOT.relative_to(ROOT)}")


def check_vendor_assets() -> None:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing vendor manifest: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    declared: set[str] = set()

    for record in manifest.get("assets", []):
        relative = str(record["path"])
        declared.add(relative)
        path = VENDOR_ROOT / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
            continue
        data = path.read_bytes()
        if len(data) != int(record["size"]):
            errors.append(f"size mismatch: {relative}")
        if _sha256(data) != str(record["sha256"]):
            errors.append(f"sha256 mismatch: {relative}")
        integrity = record.get("integrity")
        if integrity:
            try:
                _verify_sri(data, str(integrity))
            except Exception as exc:  # noqa: BLE001 - report all integrity failures together
                errors.append(f"SRI mismatch: {relative}: {exc}")

    actual = {
        path.relative_to(VENDOR_ROOT).as_posix()
        for path in VENDOR_ROOT.rglob("*")
        if path.is_file() and path != MANIFEST_PATH
    }
    undeclared = sorted(actual - declared)
    if undeclared:
        errors.append("undeclared files: " + ", ".join(undeclared))

    if errors:
        raise SystemExit("Vendor check failed:\n- " + "\n- ".join(errors))
    print(f"Vendor check passed: {len(declared)} files")


def main() -> int:
    parser = argparse.ArgumentParser(description="Vendor or verify pinned frontend assets.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Download pinned assets and rebuild the vendor manifest.")
    mode.add_argument("--check", action="store_true", help="Verify local vendored files without network access.")
    args = parser.parse_args()

    if args.write:
        write_vendor_assets()
    else:
        check_vendor_assets()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
