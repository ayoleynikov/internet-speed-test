import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from measure.cli import main
from measure.benchmark import MeasureResult
from measure.download import RequestStats


class CliTests(unittest.TestCase):
    def test_invalid_url_exits_2(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["ftp://bad"])
        self.assertEqual(code, 2)
        self.assertIn("Ошибка URL", err.getvalue())

    def test_success_prints_summary(self):
        result = MeasureResult(
            url="http://127.0.0.1:1/x",
            request_count=2,
            per_request=(
                RequestStats(512, 0.25, 200),
                RequestStats(512, 0.25, 200),
            ),
            total_bytes=1024,
            total_elapsed_seconds=0.5,
        )
        out = io.StringIO()
        with patch("measure.cli.run_benchmark", return_value=result):
            with redirect_stdout(out):
                code = main(["http://127.0.0.1:1/x", "-n", "2"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("Скачано всего", text)
        self.assertIn("MiB/s", text)

    def test_download_error_no_success_banner(self):
        from measure.download import DownloadError

        err = io.StringIO()
        out = io.StringIO()
        with patch("measure.cli.run_benchmark", side_effect=DownloadError("boom")):
            with redirect_stderr(err), redirect_stdout(out):
                code = main(["https://example.com/x"])
        self.assertEqual(code, 1)
        self.assertIn("Ошибка загрузки", err.getvalue())
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()