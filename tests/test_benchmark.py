import unittest
from unittest.mock import patch

from measure.benchmark import MeasureResult, run_benchmark
from measure.download import DownloadError, RequestStats


class BenchmarkTests(unittest.TestCase):
    def test_sequential_count_and_aggregates(self):
        calls: list[str] = []

        def fake_download(url: str, timeout: float) -> RequestStats:
            calls.append(url)
            return RequestStats(bytes_downloaded=100, elapsed_seconds=0.5, status_code=200)

        with patch("measure.benchmark.download_once", side_effect=fake_download):
            result = run_benchmark("http://example.test/file", 10, 5.0)

        self.assertEqual(len(calls), 10)
        self.assertEqual(result.total_bytes, 1000)
        self.assertAlmostEqual(result.total_elapsed_seconds, 5.0)
        self.assertAlmostEqual(result.average_request_seconds, 0.5)
        self.assertAlmostEqual(result.throughput_mib_per_s, 1000 / 5.0 / (1024**2))
        self.assertAlmostEqual(result.throughput_mbit_per_s, (1000 * 8) / 5.0 / 1_000_000)

    def test_stops_on_first_error(self):
        def fake_download(url: str, timeout: float) -> RequestStats:
            if len(fake_download.calls) == 0:  # type: ignore[attr-defined]
                fake_download.calls.append(1)  # type: ignore[attr-defined]
                return RequestStats(10, 0.1, 200)
            raise DownloadError("fail")

        fake_download.calls = []  # type: ignore[attr-defined]

        with patch("measure.benchmark.download_once", side_effect=fake_download):
            with self.assertRaises(DownloadError):
                run_benchmark("http://example.test/x", 3, 1.0)

    def test_zero_elapsed_throughput(self):
        result = MeasureResult(
            url="http://x",
            request_count=1,
            per_request=(RequestStats(0, 0.0, 200),),
            total_bytes=0,
            total_elapsed_seconds=0.0,
        )
        self.assertEqual(result.throughput_mib_per_s, 0.0)
        self.assertEqual(result.throughput_mbit_per_s, 0.0)


if __name__ == "__main__":
    unittest.main()