"""Human-readable output."""

from __future__ import annotations

from measure.benchmark import MeasureResult


def _format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024**2:
        return f"{n / 1024:.2f} KiB"
    return f"{n / (1024**2):.2f} MiB"


def format_report(result: MeasureResult) -> str:
    lines = [
        f"URL: {result.url}",
        f"Запросов: {result.request_count} (последовательно)",
        f"Скачано всего: {_format_bytes(result.total_bytes)} ({result.total_bytes} байт)",
        f"Суммарное время запросов: {result.total_elapsed_seconds:.3f} с",
        f"Среднее время одного запроса: {result.average_request_seconds:.3f} с",
    ]
    if result.total_elapsed_seconds > 0 and result.total_bytes > 0:
        lines.append(
            f"Скорость загрузки: {result.throughput_mib_per_s:.3f} MiB/s "
            f"({result.throughput_mbit_per_s:.3f} Mbit/s)"
        )
    else:
        lines.append("Скорость загрузки: 0 (нет данных или нулевое время)")
    return "\n".join(lines)