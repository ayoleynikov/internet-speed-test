"""Tiny HTTP server for deterministic tests."""

from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable


class _Handler(BaseHTTPRequestHandler):
    factory: Callable[[], tuple[int, bytes, dict[str, str] | None]] | None = None

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        assert _Handler.factory is not None
        status, body, headers = _Handler.factory()
        self.send_response(status)
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command == "GET" and status == 200:
            self.wfile.write(body)


class LocalHttpServer:
    def __init__(self, factory: Callable[[], tuple[int, bytes, dict[str, str] | None]]):
        self._factory = factory
        self._httpd: HTTPServer | None = None
        self.port = 0

    def __enter__(self) -> "LocalHttpServer":
        _Handler.factory = self._factory
        self._httpd = HTTPServer(("127.0.0.1", 0), _Handler)
        self.port = self._httpd.server_address[1]
        thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        thread.start()
        return self

    def __exit__(self, *args) -> None:
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
        _Handler.factory = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/"


def reserve_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]