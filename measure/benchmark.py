"""Sequential benchmark orchestration and aggregates."""

from __future__ import annotations

from dataclasses import dataclass

from measure.download import DownloadError, RequestStats, download_once


@dataclass(frozen=True)
class MeasureResult:
    url: str
    request_count: int
    per_request: tuple[RequestStats, ...]
    total_bytes: int
    total_elapsed_seconds: float

    @property
    def average_request_seconds(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.total_elapsed_seconds / self.request_count

    @property
    def throughput_mib_per_s(self) -> float:
        if self.total_elapsed_seconds <= 0.0:
            return 0.0
        return self.total_bytes / self.total_elapsed_seconds / (1024**2)

    @property
    def throughput_mbit_per_s(self) -> float:
        if self.total_elapsed_seconds <= 0.0:
            return 0.0
        return (self.total_bytes * 8) / self.total_elapsed_seconds / 1_000_000


def run_benchmark(url: str, request_count: int, timeout: float) -> MeasureResult:
    if request_count < 1:
        raise ValueError("Число запросов должно быть не меньше 1")

    samples: list[RequestStats] = []
    total_bytes = 0
    total_elapsed = 0.0

    for _ in range(request_count):
        stats = download_once(url, timeout)
        samples.append(stats)
        total_bytes += stats.bytes_downloaded
        total_elapsed += stats.elapsed_seconds

    return MeasureResult(
        url=url,
        request_count=request_count,
        per_request=tuple(samples),
        total_bytes=total_bytes,
        total_elapsed_seconds=total_elapsed,
    )

# Re-export for tests that patch download_once
__all__ = ["MeasureResult", "run_benchmark", "DownloadError"]