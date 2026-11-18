import unittest

from measure.download import DownloadError, download_once
from tests.local_server import LocalHttpServer

PAYLOAD = b"a" * 2048


class DownloadIntegrationTests(unittest.TestCase):
    def test_downloads_body_via_streaming(self):
        def factory():
            return 200, PAYLOAD, None

        with LocalHttpServer(factory) as server:
            stats = download_once(server.base_url, timeout=5.0)

        self.assertEqual(stats.bytes_downloaded, len(PAYLOAD))
        self.assertGreater(stats.elapsed_seconds, 0.0)
        self.assertEqual(stats.status_code, 200)

    def test_http_error_is_failure(self):
        def factory():
            return 404, b"not found", None

        with LocalHttpServer(factory) as server:
            with self.assertRaises(DownloadError) as ctx:
                download_once(server.base_url, timeout=5.0)
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_truncated_body_fails(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading

        class TruncHandler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                return

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Length", "100")
                self.end_headers()
                self.wfile.write(b"only50bytes" + b"x" * 39)  # 50 bytes, claimed 100

        httpd = HTTPServer(("127.0.0.1", 0), TruncHandler)
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaises(DownloadError) as ctx:
                download_once(f"http://127.0.0.1:{port}/", timeout=5.0)
            self.assertIn("оборвано", str(ctx.exception))
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()