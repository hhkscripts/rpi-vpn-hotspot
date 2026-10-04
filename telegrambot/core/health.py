"""Docker HTTP health check server."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegrambot.core.config import (
    BOT_HEALTH_HOST,
    BOT_HEALTH_PORT,
    BOT_SERVICE_NAME,
    logger,
)

_bot_ready = threading.Event()


def set_bot_ready(ready: bool = True) -> None:
    """Update bot readiness status."""
    if ready:
        _bot_ready.set()
    else:
        _bot_ready.clear()


class BotHealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for container health checks."""

    def do_GET(self) -> None:
        if self.path not in ["/bot-health", "/health"]:
            self.send_response(404)
            self.end_headers()
            return

        ready = _bot_ready.is_set()
        status_code = 200 if ready else 503
        payload = {
            "service": BOT_SERVICE_NAME,
            "status": "ok" if ready else "starting",
            "ready": ready,
        }
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        """Suppress standard HTTP request logging for health checks."""
        pass


def start_bot_health_server() -> ThreadingHTTPServer:
    """Start the health check HTTP server on a background thread."""
    server = ThreadingHTTPServer((BOT_HEALTH_HOST, BOT_HEALTH_PORT), BotHealthHandler)
    thread = threading.Thread(
        target=server.serve_forever,
        name="bot-health-server",
        daemon=True,
    )
    thread.start()
    logger.info(
        f"Bot health endpoint listening on "
        f"{BOT_HEALTH_HOST}:{BOT_HEALTH_PORT}/bot-health"
    )
    return server
