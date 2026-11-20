"""Integration tests for the static HTTP server (standard library only)."""

from __future__ import annotations

import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.static_server import StaticFileHandler


class StaticServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        root = Path(cls.temp_dir.name)
        (root / "index.html").write_text("<h1>Hello</h1>", encoding="utf-8")
        (root / "note.txt").write_text("Hello from test", encoding="utf-8")

        handler = partial(StaticFileHandler, directory=root)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.temp_dir.cleanup()

    def test_get_existing_file_returns_200_and_content_type(self) -> None:
        with urlopen(f"{self.base_url}/note.txt") as response:
            self.assertEqual(response.status, 200)
            self.assertTrue(response.headers["Content-Type"].startswith("text/plain"))
            self.assertEqual(response.read(), b"Hello from test")

    def test_root_returns_index(self) -> None:
        with urlopen(self.base_url + "/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Hello", response.read())

    def test_missing_file_returns_404(self) -> None:
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base_url + "/missing.txt")
        self.assertEqual(error.exception.code, 404)

    def test_post_returns_405(self) -> None:
        request = Request(self.base_url + "/", data=b"{}", method="POST")
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 405)
        self.assertEqual(error.exception.headers.get("Allow"), "GET, HEAD")

    def test_unknown_method_returns_405(self) -> None:
        request = Request(self.base_url + "/", method="BREW")
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 405)

    def test_head_returns_headers_without_body(self) -> None:
        request = Request(self.base_url + "/note.txt", method="HEAD")
        with urlopen(request) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")
            self.assertGreater(int(response.headers["Content-Length"]), 0)

    def test_path_traversal_is_blocked(self) -> None:
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base_url + "/%2e%2e/secret.txt")
        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
