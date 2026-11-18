import unittest

from measure.urls import validate_target_url


class ValidateUrlTests(unittest.TestCase):
    def test_accepts_https(self):
        self.assertEqual(
            validate_target_url("https://example.com/image.jpg"),
            "https://example.com/image.jpg",
        )

    def test_accepts_http_with_query(self):
        url = "http://127.0.0.1:9/path?x=1"
        self.assertEqual(validate_target_url(url), url)

    def test_rejects_ftp(self):
        with self.assertRaises(ValueError):
            validate_target_url("ftp://example.com/x")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            validate_target_url("   ")

    def test_rejects_missing_host(self):
        with self.assertRaises(ValueError):
            validate_target_url("https:///no-host")


if __name__ == "__main__":
    unittest.main()