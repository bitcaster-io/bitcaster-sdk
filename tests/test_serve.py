from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import contextmanager
from typing import Generator

import requests
from click.testing import CliRunner

from bitcaster_sdk.__cli__ import cli


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@contextmanager
def _serve(*extra_args: str) -> Generator[int, None, None]:
    port = _free_port()
    runner = CliRunner()

    def run() -> None:
        runner.invoke(cli, ["serve", "--port", str(port), *extra_args])

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        raise RuntimeError("Server didn't start within 5s")

    yield port


class TestServe:
    def test_get_request(self) -> None:
        with _serve() as port:
            resp = requests.get(f"http://localhost:{port}/some/path", timeout=5)
            assert resp.status_code == 200
            assert resp.json() == {}

    def test_post_with_body(self) -> None:
        with _serve() as port:
            resp = requests.post(f"http://localhost:{port}/trigger/", json={"key": "value"}, timeout=5)
            assert resp.status_code == 200
            assert resp.json() == {}

    def test_patch_request(self) -> None:
        with _serve() as port:
            resp = requests.patch(f"http://localhost:{port}/resource/1", json={"name": "updated"}, timeout=5)
            assert resp.status_code == 200

    def test_put_request(self) -> None:
        with _serve() as port:
            resp = requests.put(f"http://localhost:{port}/resource/1", json={"name": "replaced"}, timeout=5)
            assert resp.status_code == 200

    def test_empty_body(self) -> None:
        with _serve() as port:
            resp = requests.post(f"http://localhost:{port}/no-body", timeout=5)
            assert resp.status_code == 200

    def test_query_parameters(self) -> None:
        with _serve() as port:
            resp = requests.get(f"http://localhost:{port}/path?key1=val1&key2=val2", timeout=5)
            assert resp.status_code == 200

    def test_custom_response_code(self) -> None:
        with _serve("--response-code", "201") as port:
            resp = requests.post(f"http://localhost:{port}/created", json={"a": 1}, timeout=5)
            assert resp.status_code == 201
            assert resp.json() == {}

    def test_custom_response_body(self) -> None:
        body = json.dumps({"status": "ok", "id": 42})
        with _serve("--response-body", body) as port:
            resp = requests.get(f"http://localhost:{port}/test", timeout=5)
            assert resp.json() == {"status": "ok", "id": 42}

    def test_custom_code_and_body(self) -> None:
        body = json.dumps({"error": "bad request"})
        with _serve("--response-code", "400", "--response-body", body) as port:
            resp = requests.get(f"http://localhost:{port}/bad", timeout=5)
            assert resp.status_code == 400
            assert resp.json() == {"error": "bad request"}

    def test_invalid_json_response_body(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", str(_free_port()), "--response-body", "not-json"])
        assert result.exit_code != 0
        assert "Invalid JSON" in result.output

    def test_port_in_use(self) -> None:
        with _serve() as port:
            runner = CliRunner()
            result = runner.invoke(cli, ["serve", "--port", str(port)])
            assert result.exit_code != 0
            assert "Failed to start server" in result.output

    def test_malformed_content_length(self) -> None:
        with _serve() as port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect(("127.0.0.1", port))
                sock.sendall(b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: abc\r\n\r\n")
                time.sleep(0.2)
                response = sock.recv(4096)
                assert response, "Server should respond despite bad Content-Length"

    def test_non_utf8_body(self) -> None:
        with _serve() as port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect(("127.0.0.1", port))
                sock.sendall(
                    b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\n"
                    b"Content-Type: application/octet-stream\r\n\r\n\xff\xfe\x00\x01"
                )
                time.sleep(0.2)
                response = sock.recv(4096)
                assert response, "Server should respond despite non-UTF-8 body"
