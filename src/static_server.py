"""A small static HTTP server implemented with Python's standard library."""

from __future__ import annotations

import argparse
import mimetypes
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class StaticFileHandler(BaseHTTPRequestHandler):
    """Serve files from one directory. Only GET and HEAD are allowed."""

    protocol_version = "HTTP/1.1"

    def __init__(self, *args, directory: Path, **kwargs):
        self.directory = Path(directory).resolve()
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self._serve_file(send_body=True)

    def do_HEAD(self) -> None:
        self._serve_file(send_body=False)

    def do_POST(self) -> None:
        self._method_not_allowed()

    def do_PUT(self) -> None:
        self._method_not_allowed()

    def do_PATCH(self) -> None:
        self._method_not_allowed()

    def do_DELETE(self) -> None:
        self._method_not_allowed()

    def do_OPTIONS(self) -> None:
        self._method_not_allowed()

    def __getattr__(self, name: str):
        # BaseHTTPRequestHandler normally answers 501 for unknown methods.
        # For this server, every method except GET/HEAD must consistently be 405.
        if name.startswith("do_"):
            return self._method_not_allowed
        raise AttributeError(name)

    def _serve_file(self, *, send_body: bool) -> None:
        # Ignore query parameters and decode percent-encoded URL characters.
        url_path = unquote(urlsplit(self.path).path)
        relative_path = url_path.lstrip("/")
        target = (self.directory / relative_path).resolve()

        # Prevent requests such as /../../secret.txt from escaping the web root.
        try:
            target.relative_to(self.directory)
        except ValueError:
            self._send_error(404, "Not Found", send_body=send_body)
            return

        if target.is_dir():
            target = target / "index.html"

        if not target.is_file():
            self._send_error(404, "Not Found", send_body=send_body)
            return

        try:
            content = target.read_bytes()
        except OSError:
            self._send_error(404, "Not Found", send_body=send_body)
            return

        content_type, _encoding = mimetypes.guess_type(target.name)
        if content_type is None:
            content_type = "application/octet-stream"
        elif content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type += "; charset=utf-8"

        self.send_response(200, "OK")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if send_body:
            self.wfile.write(content)

    def _send_error(self, status: int, message: str, *, send_body: bool = True) -> None:
        body = f"{status} {message}\n".encode("utf-8")
        self.send_response(status, message)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if send_body:
            self.wfile.write(body)

    def _method_not_allowed(self) -> None:
        body = b"405 Method Not Allowed\n"
        self.send_response(405, "Method Not Allowed")
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        self.wfile.write(body)


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve static files over HTTP using only the Python standard library."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Interface to listen on (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="TCP port (default: 8000)")
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "public",
        help="Directory containing files to serve",
    )
    args = parser.parse_args()

    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        parser.error(f"Directory does not exist: {directory}")
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")

    handler = partial(StaticFileHandler, directory=directory)
    server = ReusableThreadingHTTPServer((args.host, args.port), handler)

    print(f"Static server is running: http://{args.host}:{args.port}")
    print(f"Serving directory: {directory}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
