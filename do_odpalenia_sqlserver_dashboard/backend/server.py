from __future__ import annotations

import json
import mimetypes
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import DB_ENGINE, DB_PATH, DOCS_DIR, FRONTEND_DIR, HOST, PORT, SQL_DIR, SQLSERVER_CONFIG
from .database import connect
from .queries import API_ROUTES


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_file(FRONTEND_DIR / "index.html")
            return
        if parsed.path.startswith("/assets/"):
            self.send_file(FRONTEND_DIR / parsed.path.lstrip("/"))
            return
        if parsed.path.startswith("/sql/"):
            self.send_file(SQL_DIR / parsed.path.replace("/sql/", "", 1))
            return
        if parsed.path.startswith("/docs/"):
            self.send_file(DOCS_DIR / parsed.path.replace("/docs/", "", 1))
            return
        if parsed.path in API_ROUTES:
            self.send_json(parsed.path, parse_qs(parsed.query))
            return
        self.send_error(404, "Not found")

    def send_json(self, route: str, params: dict[str, list[str]]) -> None:
        if DB_ENGINE == "sqlite" and not DB_PATH.exists():
            self.send_error(500, f"Database not found: {DB_PATH}")
            return
        try:
            conn = connect()
            try:
                payload = API_ROUTES[route](conn, params)
            finally:
                conn.close()
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8"))
            return
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "File not found")
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".sql":
            content_type = "text/plain; charset=utf-8"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def main() -> None:
    if DB_ENGINE == "sqlite" and not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}. Run scripts/export_sqlserver_to_sqlite.py first.")
    if DB_ENGINE == "sqlserver" and "localdb" in SQLSERVER_CONFIG["server"].lower():
        subprocess.run(["SqlLocalDB", "start", "MSSQLLocalDB"], capture_output=True)
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Dashboard running at {url}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    server.serve_forever()
