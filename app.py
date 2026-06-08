"""IPv6 Sentinel - Safe IPv6 monitoring simulator.

This application is intentionally defensive and simulation-only.
It does not capture packets, transmit packets, scan real networks,
or modify any network device or service behavior. All events and assets shown in the dashboard are
locally generated sample data for education, demos, and portfolio review.
"""

from __future__ import annotations

import hmac
import os
import random
import signal
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import psutil
from flask import Flask, Response, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from models.config_manager import Config
from models.target_manager import Target
from services.simulation_catalog import SAMPLE_ASSETS, SAMPLE_EVENTS, SCENARIO_PLAN
from services.state import MonitoringStats
from services.settings_store import SettingsStore, bounded_bool, bounded_int, bounded_text
from services.exporters import json_attachment, logs_csv_attachment
from services.diagnostics import runtime_diagnostics
from services.preflight import run_preflight_checks
from services.quality_gate import run_quality_gate
from services.api_contract import run_api_contract_check
from services.schemas import schema_contract_payload
from services.release_identity import run_release_identity_check
from services.release_artifact import run_release_artifact_check
from services.file_inventory import run_file_inventory_check
from services.manifest_hygiene import run_manifest_hygiene_check
from services.publication_hygiene import run_publication_hygiene_check
from services.gate_registry import run_gate_registry_check
from services.capability_boundary import capability_boundary_payload, run_capability_boundary_check
from services.reviewer_handoff import reviewer_handoff_payload, run_reviewer_handoff_check
from settings import (
    ALLOW_REMOTE_BIND_WITHOUT_AUTH,
    APP_NAME,
    APP_VERSION,
    DEBUG_MODE,
    FLASK_DEBUG,
    FLASK_HOST,
    FLASK_PORT,
    LOG_DIR,
    SOCKETIO_ASYNC_MODE,
    SOCKETIO_CORS_ALLOWED_ORIGINS,
    SOCKETIO_PING_INTERVAL,
    SOCKETIO_PING_TIMEOUT,
    UPDATE_INTERVAL,
    WEB_AUTH_ENABLED,
    WEB_AUTH_PASSWORD,
    WEB_AUTH_USERNAME,
    SAFE_MODE,
    SIMULATION_MODE,
    REAL_NETWORK_SCAN_ENABLED,
    REAL_PACKET_CAPTURE_ENABLED,
    REAL_PACKET_SEND_ENABLED,
)
from utils.logger import setup_logger
from utils.performance_monitor import PerformanceMonitor


class IPv6SentinelApp:
    """Local-only monitoring simulator with a Flask/Socket.IO dashboard."""

    def __init__(self) -> None:
        self.logger = setup_logger("IPv6Sentinel")
        self.config = Config()
        self.app = Flask(__name__)
        self.app.config.update(
            SECRET_KEY=os.environ.get("IPV6_SENTINEL_SECRET_KEY", os.urandom(24).hex()),
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            JSON_SORT_KEYS=False,
            MAX_CONTENT_LENGTH=64 * 1024,
        )
        self.socketio = SocketIO(
            self.app,
            async_mode=SOCKETIO_ASYNC_MODE,
            cors_allowed_origins=SOCKETIO_CORS_ALLOWED_ORIGINS,
            ping_timeout=SOCKETIO_PING_TIMEOUT,
            ping_interval=SOCKETIO_PING_INTERVAL,
        )
        self.performance_monitor = PerformanceMonitor()
        self.stats = MonitoringStats()
        self.assets: Dict[str, Target] = {}
        self.connected_clients: Set[str] = set()
        self.event_log: List[dict] = []
        self.simulation_speed = 5
        self.running = False
        self.monitoring_active = False
        self._signals_installed = False
        self._lock = threading.RLock()
        self._simulation_thread: Optional[threading.Thread] = None
        self._ui_thread: Optional[threading.Thread] = None
        self.data_dir = Path(os.environ.get("IPV6_SENTINEL_DATA_DIR", "data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ui_settings_path = self.data_dir / "ui_settings.json"
        self.settings_store = SettingsStore(self.ui_settings_path)
        self.ui_settings = self._load_ui_settings()
        self.simulation_speed = int(self.ui_settings.get("simulation_speed", 5))

        self._validate_startup_security()
        self._setup_auth()
        self._setup_security_headers()
        self._setup_routes()
        self._setup_error_handlers()
        self._setup_socket_events()


    @staticmethod
    def _is_loopback_host(host: str) -> bool:
        normalized = (host or "").strip().lower()
        return normalized in {"127.0.0.1", "localhost", "::1"}

    def _validate_startup_security(self) -> None:
        """Fail closed when a user accidentally exposes the dashboard without auth."""
        remote_bind = not self._is_loopback_host(FLASK_HOST)
        if remote_bind and not ALLOW_REMOTE_BIND_WITHOUT_AUTH:
            if not WEB_AUTH_ENABLED or not WEB_AUTH_PASSWORD:
                raise RuntimeError(
                    "Refusing to bind IPv6 Sentinel Safe beyond localhost without authentication. "
                    "Set IPV6_SENTINEL_WEB_AUTH_ENABLED=1 and IPV6_SENTINEL_PASSWORD, "
                    "or explicitly set IPV6_SENTINEL_ALLOW_INSECURE_REMOTE=1 for a controlled lab demo."
                )
        if "*" in SOCKETIO_CORS_ALLOWED_ORIGINS and not ALLOW_REMOTE_BIND_WITHOUT_AUTH:
            raise RuntimeError(
                "Wildcard CORS is disabled by default. Set explicit origins through IPV6_SENTINEL_CORS, "
                "or use IPV6_SENTINEL_ALLOW_INSECURE_REMOTE=1 only in a controlled local lab."
            )

    def _setup_signal_handlers(self) -> None:
        """Register shutdown hooks only when the server is actually started.

        App construction is used by unit tests, scripts, and embedding contexts.
        Installing global signal handlers during construction makes those contexts
        noisy and can interfere with subprocess-based validation. The app keeps object
        creation side-effect-light and installs handlers at start() time only.
        """
        if self._signals_installed:
            return
        if threading.current_thread() is not threading.main_thread():
            self.logger.debug("Signal handlers were not installed outside the main thread.")
            return

        def signal_handler(signum: int, _frame: Any) -> None:
            self.logger.info("종료 신호 수신: %s", signum)
            self.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        self._signals_installed = True

    def _setup_auth(self) -> None:
        @self.app.before_request
        def require_basic_auth() -> Response | None:
            if not WEB_AUTH_ENABLED:
                return None
            if request.endpoint == "static":
                return None
            if not WEB_AUTH_PASSWORD:
                return Response(
                    "IPV6_SENTINEL_PASSWORD 환경변수를 먼저 설정하세요.",
                    503,
                    {"Content-Type": "text/plain; charset=utf-8"},
                )
            auth = request.authorization
            username_ok = auth and hmac.compare_digest(auth.username or "", WEB_AUTH_USERNAME)
            password_ok = auth and hmac.compare_digest(auth.password or "", WEB_AUTH_PASSWORD)
            if username_ok and password_ok:
                return None
            return Response(
                "인증이 필요합니다.",
                401,
                {"WWW-Authenticate": 'Basic realm="IPv6 Sentinel"'},
            )


    def _setup_security_headers(self) -> None:
        @self.app.after_request
        def add_security_headers(response: Response) -> Response:
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault("Referrer-Policy", "no-referrer")
            response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
            if request.path.startswith("/api/"):
                response.headers.setdefault("Cache-Control", "no-store")
            return response

    def _setup_routes(self) -> None:
        @self.app.route("/")
        def home() -> str:
            return render_template("index.html", app_name=APP_NAME, app_version=APP_VERSION)

        @self.app.route("/api/health")
        def health() -> Response:
            return jsonify({"status": "ok", "mode": "safe_simulation", "version": APP_VERSION})

        @self.app.route("/api/ready")
        def ready() -> Response:
            payload, status_code = self._readiness_status()
            return jsonify(payload), status_code

        @self.app.route("/api/info")
        def info() -> Response:
            return jsonify(self._app_info())

        @self.app.route("/api/snapshot.json")
        def export_snapshot_json() -> Response:
            return json_attachment(self._snapshot(), "ipv6-sentinel-snapshot")

        @self.app.route("/api/report.json")
        def export_portfolio_report() -> Response:
            return json_attachment(self._portfolio_report(), "ipv6-sentinel-portfolio-report")

        @self.app.route("/api/diagnostics")
        def diagnostics() -> Response:
            return jsonify(self._diagnostics())

        @self.app.route("/api/preflight")
        def preflight() -> Response:
            payload = self._preflight()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/quality")
        def quality_gate() -> Response:
            payload = self._quality_gate()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/contract")
        def api_contract() -> Response:
            payload = self._api_contract()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/schema")
        def schema_contract() -> Response:
            return jsonify(schema_contract_payload())

        @self.app.route("/api/release")
        def release_identity() -> Response:
            payload = self._release_identity()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/artifact")
        def release_artifact() -> Response:
            payload = self._release_artifact()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/integrity")
        def file_inventory_integrity() -> Response:
            payload = self._file_inventory()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/manifest")
        def manifest_hygiene() -> Response:
            payload = self._manifest_hygiene()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/publication")
        def publication_hygiene() -> Response:
            payload = self._publication_hygiene()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/gates")
        def gate_registry() -> Response:
            payload = self._gate_registry()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/capabilities")
        def capabilities() -> Response:
            payload = self._capabilities()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/reviewer")
        def reviewer_handoff() -> Response:
            payload = self._reviewer_handoff()
            return jsonify(payload), 200 if payload["status"] == "pass" else 503

        @self.app.route("/api/stats")
        def get_stats() -> Response:
            return jsonify(self._stats_snapshot())

        @self.app.route("/api/assets")
        def get_assets() -> Response:
            return jsonify(self._asset_list())

        @self.app.route("/api/assets/<path:asset_id>")
        def get_asset(asset_id: str) -> Response:
            asset = self._get_asset(asset_id)
            if not asset:
                return jsonify({"error": "asset_not_found"}), 404
            return jsonify(asset)

        @self.app.route("/api/performance")
        def get_performance() -> Response:
            return jsonify(self.performance_monitor.snapshot())

        @self.app.route("/api/logs")
        def get_logs() -> Response:
            return jsonify(self._recent_logs())

        @self.app.route("/api/logs.csv")
        def export_logs_csv() -> Response:
            return logs_csv_attachment(self._recent_logs())

        @self.app.route("/api/monitoring/start", methods=["POST"])
        def start_monitoring_rest() -> Response:
            self.running = True
            self.start_monitoring()
            self._broadcast_state()
            return jsonify({
                "status": "started",
                "mode": "safe_simulation",
                "stats": self._stats_snapshot(),
                "assets": self._asset_list(),
            })

        @self.app.route("/api/monitoring/stop", methods=["POST"])
        def stop_monitoring_rest() -> Response:
            self.stop_monitoring()
            self._broadcast_state()
            return jsonify({
                "status": "stopped",
                "mode": "safe_simulation",
                "stats": self._stats_snapshot(),
                "assets": self._asset_list(),
            })

        @self.app.route("/api/assets/generate", methods=["POST"])
        def generate_assets_rest() -> Response:
            assets = self.generate_sample_asset_inventory_sync()
            self._broadcast_state()
            return jsonify({
                "status": "completed",
                "mode": "safe_simulation",
                "assets": assets,
                "stats": self._stats_snapshot(),
                "logs": self._recent_logs(),
            })

        @self.app.route("/api/logs/clear", methods=["POST"])
        def clear_logs_rest() -> Response:
            with self._lock:
                self.event_log.clear()
            self.socketio.emit("logs_cleared", {"status": "completed"})
            return jsonify({"status": "cleared", "logs": self._recent_logs()})

        @self.app.route("/api/simulation/speed", methods=["POST"])
        def set_simulation_speed_rest() -> Response:
            payload = request.get_json(silent=True) or {}
            self.simulation_speed = self._bounded_int(payload.get("speed"), self.simulation_speed, 1, 10)
            settings = self._update_ui_settings({"simulation_speed": self.simulation_speed})
            self.socketio.emit("simulation_speed_updated", {"speed": self.simulation_speed})
            return jsonify({"status": "updated", "speed": self.simulation_speed, "settings": settings})

        @self.app.route("/api/reset", methods=["POST"])
        def reset_simulation() -> Response:
            self.reset_simulation()
            self._broadcast_state()
            self.socketio.emit("logs_cleared", {"status": "completed"})
            return jsonify({"status": "reset", "stats": self._stats_snapshot(), "assets": self._asset_list()})

        @self.app.route("/api/demo/scenario", methods=["POST"])
        def seed_demo_scenario() -> Response:
            payload = self.seed_demo_scenario()
            self._broadcast_state()
            return jsonify(payload)

        @self.app.route("/api/settings", methods=["GET", "POST"])
        def settings() -> Response:
            if request.method == "GET":
                return jsonify(self.ui_settings)
            payload = request.get_json(silent=True) or {}
            updated = self._update_ui_settings(payload)
            self.socketio.emit("settings_updated", updated)
            self._emit_log(
                "settings_updated",
                "local-dashboard",
                "success",
                "대시보드 설정이 저장되었습니다.",
                {"settings": updated},
            )
            return jsonify(updated)


    def _setup_error_handlers(self) -> None:
        @self.app.errorhandler(404)
        def not_found(_error: Exception) -> Response | tuple[Response, int]:
            if request.path.startswith("/api/"):
                return jsonify({"error": "not_found", "path": request.path}), 404
            return jsonify({"error": "not_found"}), 404

        @self.app.errorhandler(500)
        def internal_error(error: Exception) -> Response | tuple[Response, int]:
            self.logger.exception("처리되지 않은 서버 오류: %s", error)
            return jsonify({"error": "internal_server_error"}), 500

    def _setup_socket_events(self) -> None:
        @self.socketio.on("connect")
        def handle_connect() -> None:
            self.connected_clients.add(request.sid)
            emit(
                "connected",
                {
                    "status": "connected",
                    "mode": "safe_simulation",
                    "stats": self._stats_snapshot(),
                    "assets": self._asset_list(),
                    "settings": self.ui_settings,
                    "timestamp": time.time(),
                },
            )
            self._emit_log("system", "local-dashboard", "info", "안전 모드로 연결되었습니다.")

        @self.socketio.on("disconnect")
        def handle_disconnect() -> None:
            self.connected_clients.discard(request.sid)

        @self.socketio.on("start_monitoring")
        def handle_start_monitoring(_data: Any = None) -> None:
            self.start_monitoring()
            emit(
                "monitoring_status",
                {
                    "status": "started",
                    "message": "안전한 모니터링 시뮬레이션이 시작되었습니다.",
                    "mode": "safe_simulation",
                },
            )

        @self.socketio.on("stop_monitoring")
        def handle_stop_monitoring(_data: Any = None) -> None:
            self.stop_monitoring()
            emit(
                "monitoring_status",
                {
                    "status": "stopped",
                    "message": "모니터링 시뮬레이션이 중지되었습니다.",
                    "mode": "safe_simulation",
                },
            )

        @self.socketio.on("set_simulation_speed")
        def handle_simulation_speed(data: Any = None) -> None:
            raw_value = data.get("speed", self.simulation_speed) if isinstance(data, dict) else self.simulation_speed
            self.simulation_speed = max(1, min(10, int(raw_value)))
            self._update_ui_settings({"simulation_speed": self.simulation_speed})
            emit("simulation_speed_updated", {"speed": self.simulation_speed})
            self._emit_log("system", "local-dashboard", "info", f"시뮬레이션 속도 {self.simulation_speed}단계 적용")

        @self.socketio.on("generate_sample_assets")
        def handle_generate_sample_assets(_data: Any = None) -> None:
            emit("inventory_status", {"status": "running", "message": "샘플 자산 목록을 생성합니다."})
            threading.Thread(target=self._generate_sample_asset_inventory, daemon=True).start()

        @self.socketio.on("request_update")
        def handle_request_update(_data: Any = None) -> None:
            emit("stats_update", self._stats_snapshot())
            emit("assets_update", self._asset_list())

        @self.socketio.on("request_stats")
        def handle_request_stats(_data: Any = None) -> None:
            emit("stats_update", self._stats_snapshot())

        @self.socketio.on("request_performance")
        def handle_request_performance(_data: Any = None) -> None:
            emit("performance_update", self.performance_monitor.snapshot())

        @self.socketio.on("clear_logs")
        def handle_clear_logs(_data: Any = None) -> None:
            with self._lock:
                self.event_log.clear()
            emit("logs_cleared", {"status": "completed"})

        @self.socketio.on("reset_simulation")
        def handle_reset_simulation(_data: Any = None) -> None:
            self.reset_simulation()
            emit("logs_cleared", {"status": "completed"})
            emit("stats_update", self._stats_snapshot())
            emit("assets_update", self._asset_list())

        @self.socketio.on("seed_demo_scenario")
        def handle_seed_demo_scenario(_data: Any = None) -> None:
            payload = self.seed_demo_scenario()
            emit("demo_scenario_seeded", payload)
            emit("stats_update", self._stats_snapshot())
            emit("assets_update", self._asset_list())


    def _readiness_status(self) -> tuple[Dict[str, Any], int]:
        checks = {
            "safe_mode": bool(SAFE_MODE),
            "simulation_mode": bool(SIMULATION_MODE),
            "real_packet_capture_disabled": not REAL_PACKET_CAPTURE_ENABLED,
            "real_packet_send_disabled": not REAL_PACKET_SEND_ENABLED,
            "real_network_scan_disabled": not REAL_NETWORK_SCAN_ENABLED,
            "local_or_auth_protected": self._is_loopback_host(FLASK_HOST) or (WEB_AUTH_ENABLED and bool(WEB_AUTH_PASSWORD)),
        }
        ready = all(checks.values())
        return {"status": "ready" if ready else "not_ready", "checks": checks, "version": APP_VERSION}, 200 if ready else 503

    def _app_info(self) -> Dict[str, Any]:
        return {
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "mode": "safe_simulation",
            "safe_mode": SAFE_MODE,
            "simulation_mode": SIMULATION_MODE,
            "real_packet_capture_enabled": REAL_PACKET_CAPTURE_ENABLED,
            "real_packet_send_enabled": REAL_PACKET_SEND_ENABLED,
            "real_network_scan_enabled": REAL_NETWORK_SCAN_ENABLED,
            "auth_enabled": WEB_AUTH_ENABLED,
            "bind_host": FLASK_HOST,
            "bind_port": FLASK_PORT,
            "cors_origins": SOCKETIO_CORS_ALLOWED_ORIGINS,
        }

    def _diagnostics(self) -> Dict[str, Any]:
        readiness, readiness_code = self._readiness_status()
        diagnostics = runtime_diagnostics(
            safe_mode=SAFE_MODE,
            simulation_mode=SIMULATION_MODE,
            packet_flags={
                "capture": REAL_PACKET_CAPTURE_ENABLED,
                "send": REAL_PACKET_SEND_ENABLED,
                "scan": REAL_NETWORK_SCAN_ENABLED,
            },
            auth_enabled=WEB_AUTH_ENABLED,
            local_or_auth_protected=readiness["checks"]["local_or_auth_protected"],
            app_root=Path(__file__).resolve().parent,
        )
        diagnostics.update({
            "readiness_status": readiness["status"],
            "readiness_code": readiness_code,
            "version": APP_VERSION,
            "mode": "safe_simulation",
        })
        return diagnostics

    def _preflight(self) -> Dict[str, Any]:
        return run_preflight_checks(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
            safe_mode=SAFE_MODE,
            simulation_mode=SIMULATION_MODE,
            real_packet_flags={
                "capture": REAL_PACKET_CAPTURE_ENABLED,
                "send": REAL_PACKET_SEND_ENABLED,
                "scan": REAL_NETWORK_SCAN_ENABLED,
            },
            host=FLASK_HOST,
            port=FLASK_PORT,
            auth_enabled=WEB_AUTH_ENABLED,
            auth_password_set=bool(WEB_AUTH_PASSWORD),
            cors_origins=SOCKETIO_CORS_ALLOWED_ORIGINS,
        )


    def _quality_gate(self) -> Dict[str, Any]:
        return run_quality_gate(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _api_contract(self) -> Dict[str, Any]:
        return run_api_contract_check(app_root=Path(__file__).resolve().parent)

    def _release_identity(self) -> Dict[str, Any]:
        return run_release_identity_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _release_artifact(self) -> Dict[str, Any]:
        return run_release_artifact_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _file_inventory(self) -> Dict[str, Any]:
        return run_file_inventory_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _manifest_hygiene(self) -> Dict[str, Any]:
        return run_manifest_hygiene_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _publication_hygiene(self) -> Dict[str, Any]:
        return run_publication_hygiene_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _gate_registry(self) -> Dict[str, Any]:
        return run_gate_registry_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _capabilities(self) -> Dict[str, Any]:
        return run_capability_boundary_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _reviewer_handoff(self) -> Dict[str, Any]:
        return run_reviewer_handoff_check(
            app_root=Path(__file__).resolve().parent,
            app_version=APP_VERSION,
        )

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "info": self._app_info(),
            "stats": self._stats_snapshot(),
            "assets": self._asset_list(),
            "logs": self._recent_logs(),
            "settings": dict(self.ui_settings),
        }

    def _portfolio_report(self) -> Dict[str, Any]:
        """Return a reviewer-friendly summary without exposing host secrets."""
        snapshot = self._snapshot()
        checks, status_code = self._readiness_status()
        return {
            "generated_at": snapshot["generated_at"],
            "project": {
                "name": APP_NAME,
                "version": APP_VERSION,
                "category": "defensive_ipv6_monitoring_simulator",
                "audience": ["portfolio_review", "security_training", "local_demo"],
            },
            "safety": {
                "ready": status_code == 200,
                "checks": checks["checks"],
                "diagnostics": self._diagnostics(),
                "preflight": self._preflight(),
                "quality_gate": self._quality_gate(),
                "api_contract": self._api_contract(),
                "schema_contract": schema_contract_payload(),
                "release_artifact": self._release_artifact(),
                "file_inventory": self._file_inventory(),
                "manifest_hygiene": self._manifest_hygiene(),
                "publication_hygiene": self._publication_hygiene(),
                "capability_boundary": self._capabilities(),
                "real_packet_capture_enabled": REAL_PACKET_CAPTURE_ENABLED,
                "real_packet_send_enabled": REAL_PACKET_SEND_ENABLED,
                "real_network_scan_enabled": REAL_NETWORK_SCAN_ENABLED,
            },
            "demo_summary": {
                "asset_count": len(snapshot["assets"]),
                "log_count": len(snapshot["logs"]),
                "stats": snapshot["stats"],
                "recommended_flow": [
                    "데모 시나리오 실행",
                    "자산 상세 모달 확인",
                    "스냅샷 JSON 또는 포트폴리오 리포트 저장",
                    "SECURITY.md와 SECURITY_CHECKLIST.md로 안전 설계 설명",
                ],
            },
            "limitations": [
                "실제 네트워크 캡처/스캔/패킷 송신은 의도적으로 비활성화되어 있습니다.",
                "표시 데이터는 로컬에서 생성되는 교육용 샘플입니다.",
                "운영 배포가 아니라 포트폴리오·교육·시연 목적의 안전형 MVP입니다.",
            ],
        }

    @staticmethod
    def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
        return bounded_int(value, default, minimum, maximum)

    @staticmethod
    def _bounded_text(value: Any, default: str, max_length: int = 80) -> str:
        return bounded_text(value, default, max_length)

    @staticmethod
    def _bounded_bool(value: Any, default: bool) -> bool:
        return bounded_bool(value, default)

    @staticmethod
    def _net_total_mb() -> float:
        try:
            counters = psutil.net_io_counters()
        except Exception:
            return 0.0
        if counters is None:
            return 0.0
        return (getattr(counters, "bytes_sent", 0) + getattr(counters, "bytes_recv", 0)) / 1024 / 1024

    def _load_ui_settings(self) -> Dict[str, Any]:
        self.settings_store = SettingsStore(self.ui_settings_path)
        return self.settings_store.load()

    def _update_ui_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.settings_store = SettingsStore(self.ui_settings_path)
        self.ui_settings = self.settings_store.save(payload, self.ui_settings)
        self.simulation_speed = int(self.ui_settings.get("simulation_speed", self.simulation_speed))
        return dict(self.ui_settings)

    def _stats_snapshot(self) -> Dict[str, float | int]:
        with self._lock:
            try:
                self.stats.memory_usage = float(psutil.virtual_memory().percent)
            except Exception:
                self.stats.memory_usage = 0.0
            try:
                self.stats.cpu_usage = float(psutil.cpu_percent(interval=None))
            except Exception:
                self.stats.cpu_usage = 0.0
            self.stats.network_total_mb = self._net_total_mb()
            self.stats.active_assets = len(self.assets)
            return self.stats.to_dict()

    def _asset_list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [asset.to_dict() for asset in sorted(self.assets.values(), key=lambda item: item.host)]

    def _get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for key, asset in self.assets.items():
                if asset_id in {key, asset.mac, asset.host}:
                    return asset.to_dict()
        return None

    def _recent_logs(self) -> List[dict]:
        retention = int(self.ui_settings.get("event_retention", 300))
        with self._lock:
            return self.event_log[-retention:]

    def _emit_log(self, event_type: str, asset: str, status: str, message: str, details: Optional[dict] = None) -> None:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "asset": asset,
            "status": status,
            "message": message,
            "details": {"safe_mode": True, **(details or {})},
        }
        with self._lock:
            self.event_log.append(log_entry)
            retention = int(self.ui_settings.get("event_retention", 300))
            if len(self.event_log) > max(500, retention * 2):
                self.event_log = self.event_log[-retention:]
        self.logger.info("[%s] %s - %s", event_type, asset, message)
        if self.connected_clients:
            self.socketio.emit("monitoring_log", log_entry)

    def start_monitoring(self) -> None:
        if self.monitoring_active:
            self._emit_log("system", "local-dashboard", "info", "이미 모니터링 중입니다.")
            return
        self.monitoring_active = True
        self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._simulation_thread.start()
        self._emit_log("system", "local-dashboard", "success", "안전 모니터링 시뮬레이션 시작")

    def stop_monitoring(self) -> None:
        self.monitoring_active = False
        self._emit_log("system", "local-dashboard", "warning", "안전 모니터링 시뮬레이션 중지")

    def _simulation_loop(self) -> None:
        while self.monitoring_active and self.running:
            delay = max(0.4, 3.0 - (self.simulation_speed * 0.22))
            self._simulate_one_event()
            self._broadcast_state()
            time.sleep(delay)

    def _simulate_one_event(self) -> None:
        event = random.choice(SAMPLE_EVENTS)
        sample = random.choice(SAMPLE_ASSETS)
        asset = self._ensure_asset(sample)
        event_type = event["event_type"]
        with self._lock:
            asset.update_last_seen()
            self.stats.total_events += 1
            if event_type == "dhcpv6_observed":
                self.stats.dhcpv6_observations += 1
            elif event_type == "dns_observed":
                self.stats.dns_observations += 1
            elif event_type == "neighbor_discovery_observed":
                self.stats.nd_observations += 1
            elif event_type == "suspicious_pattern_detected" and self.ui_settings.get("threat_detection", True):
                self.stats.suspicious_events += 1
            elif event_type == "policy_response_simulated" and self.ui_settings.get("policy_response_enabled", True):
                self.stats.policy_response_events += 1
        self._emit_log(
            event_type,
            asset.host,
            event["severity"],
            event["title"],
            {
                "ipv6": asset.ipv6,
                "mac": asset.mac,
                "recommendation": event["recommendation"],
            },
        )

    def _ensure_asset(self, sample: Dict[str, Any]) -> Target:
        with self._lock:
            mac = sample["mac"]
            if mac not in self.assets:
                self.assets[mac] = Target(
                    mac=mac,
                    host=sample["host"],
                    ipv4=sample.get("ipv4", ""),
                    ipv6=sample.get("ipv6", ""),
                    status="observed",
                    metadata={"role": sample.get("role", "Unknown"), "risk_level": sample.get("risk_level", "LOW")},
                )
            return self.assets[mac]

    def generate_sample_asset_inventory_sync(self) -> List[Dict[str, Any]]:
        """Create deterministic local sample assets without requiring Socket.IO."""
        for sample in SAMPLE_ASSETS:
            asset = self._ensure_asset(sample)
            with self._lock:
                asset.update_last_seen()
                self.stats.total_events += 1
        self._emit_log("asset_inventory", "local-dashboard", "success", "샘플 자산 목록 생성 완료")
        return self._asset_list()

    def _generate_sample_asset_inventory(self) -> None:
        total = len(SAMPLE_ASSETS)
        for index, sample in enumerate(SAMPLE_ASSETS, start=1):
            time.sleep(0.2)
            asset = self._ensure_asset(sample)
            with self._lock:
                asset.update_last_seen()
                self.stats.total_events += 1
            self.socketio.emit("inventory_progress", {"progress": (index / total) * 100, "processed": index, "total": total})
            self.socketio.emit("asset_discovered", asset.to_dict())
        self._broadcast_state()
        self.socketio.emit("inventory_status", {"status": "completed", "message": "샘플 자산 목록 생성 완료"})
        self._emit_log("asset_inventory", "local-dashboard", "success", "샘플 자산 목록 생성 완료")

    def _broadcast_state(self) -> None:
        if self.connected_clients:
            self.socketio.emit("stats_update", self._stats_snapshot())
            self.socketio.emit("assets_update", self._asset_list())

    def _ui_loop(self) -> None:
        while self.running:
            self._broadcast_state()
            time.sleep(max(1, UPDATE_INTERVAL))

    def seed_demo_scenario(self) -> Dict[str, Any]:
        """Load a deterministic local-only demo scenario for portfolio presentations."""
        with self._lock:
            self.assets.clear()
            self.event_log.clear()
            self.stats = MonitoringStats()

        for sample in SAMPLE_ASSETS:
            asset = self._ensure_asset(sample)
            asset.update_last_seen()

        scenario_plan = SCENARIO_PLAN
        event_by_type = {event["event_type"]: event for event in SAMPLE_EVENTS}

        for event_type, asset_index in scenario_plan:
            event = event_by_type[event_type]
            asset = self._ensure_asset(SAMPLE_ASSETS[asset_index])
            with self._lock:
                asset.update_last_seen()
                self.stats.total_events += 1
                if event_type == "dhcpv6_observed":
                    self.stats.dhcpv6_observations += 1
                elif event_type == "dns_observed":
                    self.stats.dns_observations += 1
                elif event_type == "neighbor_discovery_observed":
                    self.stats.nd_observations += 1
                elif event_type == "suspicious_pattern_detected":
                    self.stats.suspicious_events += 1
                elif event_type == "policy_response_simulated":
                    self.stats.policy_response_events += 1
            self._emit_log(
                event_type,
                asset.host,
                event["severity"],
                f"데모 시나리오: {event['title']}",
                {"ipv6": asset.ipv6, "mac": asset.mac, "recommendation": event["recommendation"]},
            )

        self._emit_log("demo_scenario", "local-dashboard", "success", "포트폴리오 데모 시나리오가 준비되었습니다.")
        self._broadcast_state()
        return {
            "status": "seeded",
            "scenario": "portfolio_demo",
            "assets": self._asset_list(),
            "stats": self._stats_snapshot(),
            "logs": self._recent_logs(),
        }

    def reset_simulation(self) -> None:
        """Clear local sample data and counters without touching the host network."""
        with self._lock:
            self.assets.clear()
            self.event_log.clear()
            self.stats = MonitoringStats()
        self._emit_log("system", "local-dashboard", "success", "시뮬레이션 데이터가 초기화되었습니다.")

    def start(self) -> None:
        self._setup_signal_handlers()
        self.running = True
        self.logger.info("%s %s 시작: http://%s:%s", APP_NAME, APP_VERSION, FLASK_HOST, FLASK_PORT)
        self._ui_thread = threading.Thread(target=self._ui_loop, daemon=True)
        self._ui_thread.start()
        self.socketio.run(
            self.app,
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG or DEBUG_MODE,
            use_reloader=False,
            allow_unsafe_werkzeug=DEBUG_MODE or self._is_loopback_host(FLASK_HOST),
        )

    def shutdown(self) -> None:
        self.monitoring_active = False
        self.running = False
        for worker in (self._simulation_thread, self._ui_thread):
            if worker and worker.is_alive() and worker is not threading.current_thread():
                worker.join(timeout=1.0)
        self.performance_monitor.shutdown()
        self.logger.info("%s 종료", APP_NAME)


def main() -> None:
    app = IPv6SentinelApp()
    app.start()


if __name__ == "__main__":
    main()
