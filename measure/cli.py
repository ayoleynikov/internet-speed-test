"""Command-line entrypoint."""

from __future__ import annotations

import argparse
import sys

from measure.benchmark import run_benchmark
from measure.download import DownloadError
from measure.formatting import format_report
from measure.urls import validate_target_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="measure",
        description="10 последовательных HTTP(S)-загрузок и замер скорости.",
    )
    parser.add_argument("url", help="Целевой URL (например, ссылка на изображение)")
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        metavar="N",
        help="Число последовательных запросов (по умолчанию: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        metavar="SEC",
        help="Таймаут одного запроса в секундах (по умолчанию: 60)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.count < 1:
        print("Ошибка: --count должен быть >= 1", file=sys.stderr)
        return 2
    if args.timeout <= 0 or not (args.timeout < float("inf")):
        print("Ошибка: --timeout должен быть конечным положительным числом", file=sys.stderr)
        return 2

    try:
        url = validate_target_url(args.url)
    except ValueError as exc:
        print(f"Ошибка URL: {exc}", file=sys.stderr)
        return 2

    try:
        result = run_benchmark(url, args.count, args.timeout)
    except DownloadError as exc:
        print(f"Ошибка загрузки: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2

    print(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())