"""Single HTTP(S) download with streamed byte counting."""

from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from time import perf_counter
from typing import BinaryIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CHUNK_SIZE = 64 * 1024


@dataclass(frozen=True)
class RequestStats:
    bytes_downloaded: int
    elapsed_seconds: float
    status_code: int | None


class DownloadError(Exception):
    """Incomplete or failed download."""

    def __init__(self, message: str, *, partial_bytes: int = 0, elapsed: float = 0.0):
        super().__init__(message)
        self.partial_bytes = partial_bytes
        self.elapsed = elapsed


def _read_body_streaming(resp: BinaryIO) -> int:
    total = 0
    while True:
        try:
            chunk = resp.read(CHUNK_SIZE)
        except socket.timeout as exc:
            raise DownloadError("Таймаут при чтении тела ответа") from exc
        if not chunk:
            break
        total += len(chunk)
    return total


def download_once(url: str, timeout: float) -> RequestStats:
    """
    Time one GET from connection start through full body read.
    Bytes counted from the wire via streaming reads, not Content-Length.
    """
    ctx = ssl.create_default_context()
    req = Request(url, method="GET", headers={"User-Agent": "measure-speed-cli/1.0"})
    started = perf_counter()

    try:
        resp = urlopen(req, timeout=timeout, context=ctx)
    except HTTPError as exc:
        elapsed = perf_counter() - started
        # Do not treat error responses as a successful benchmark sample.
        raise DownloadError(
            f"HTTP {exc.code}: {exc.reason}",
            partial_bytes=0,
            elapsed=elapsed,
        ) from exc
    except URLError as exc:
        elapsed = perf_counter() - started
        raise DownloadError(f"Сетевая ошибка: {exc.reason}", elapsed=elapsed) from exc
    except socket.timeout as exc:
        elapsed = perf_counter() - started
        raise DownloadError("Таймаут при установке соединения", elapsed=elapsed) from exc

    status = getattr(resp, "status", None) or resp.getcode()

    try:
        with resp:
            body_bytes = _read_body_streaming(resp)
            raw_length = resp.headers.get("Content-Length")
            if raw_length is not None:
                try:
                    expected = int(raw_length)
                except ValueError:
                    expected = None
                if expected is not None and body_bytes < expected:
                    raise DownloadError(
                        f"Тело ответа оборвано: получено {body_bytes} байт, ожидалось {expected}"
                    )
    except DownloadError:
        elapsed = perf_counter() - started
        raise
    except Exception as exc:
        elapsed = perf_counter() - started
        raise DownloadError(f"Ошибка при чтении ответа: {exc}", elapsed=elapsed) from exc

    elapsed = perf_counter() - started
    return RequestStats(bytes_downloaded=body_bytes, elapsed_seconds=elapsed, status_code=status)