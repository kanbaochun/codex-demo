from __future__ import annotations

import cgi
import json
import os
import posixpath
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
PDF_DIR = BASE_DIR / "pdf_path"


class PageIndexHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/files":
            self.handle_list_files(parsed.query)
            return
        if path.startswith("/api/json/"):
            self.handle_json_file(path)
            return
        if path.startswith("/api/pdf/"):
            self.handle_pdf_file(path)
            return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/upload":
            self.send_error(HTTPStatus.NOT_FOUND, "Unsupported API endpoint")
            return

        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_error(HTTPStatus.BAD_REQUEST, "Only multipart/form-data is supported")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
            },
        )

        upload_kind = (form.getvalue("kind") or "").strip().lower()
        file_item = form["file"] if "file" in form else None
        if not file_item or not getattr(file_item, "filename", ""):
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing file")
            return

        target_dir: Path
        expected_suffixes: tuple[str, ...]
        if upload_kind == "json":
            target_dir = RESULTS_DIR
            expected_suffixes = (".json",)
        elif upload_kind == "pdf":
            target_dir = PDF_DIR
            expected_suffixes = (".pdf",)
        else:
            self.send_error(HTTPStatus.BAD_REQUEST, "kind must be json or pdf")
            return

        filename = os.path.basename(file_item.filename)
        suffix = Path(filename).suffix.lower()
        if suffix not in expected_suffixes:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                f"Invalid file extension: {suffix or '<none>'}",
            )
            return

        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename

        with open(target_path, "wb") as out:
            out.write(file_item.file.read())

        self.send_json(
            {
                "ok": True,
                "filename": filename,
                "kind": upload_kind,
                "saved_to": str(target_path.relative_to(BASE_DIR)),
            }
        )

    def translate_path(self, path: str) -> str:
        # Keep SimpleHTTPRequestHandler behavior for static files from BASE_DIR.
        path = path.split("?", 1)[0]
        path = path.split("#", 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = [word for word in path.split("/") if word]
        translated = str(BASE_DIR)
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                continue
            translated = os.path.join(translated, word)
        return translated

    def handle_list_files(self, query: str) -> None:
        params = urllib.parse.parse_qs(query)
        file_type = (params.get("type", [""])[0] or "").lower()

        if file_type == "json":
            directory = RESULTS_DIR
            suffixes = (".json",)
        elif file_type == "pdf":
            directory = PDF_DIR
            suffixes = (".pdf",)
        else:
            self.send_error(HTTPStatus.BAD_REQUEST, "type must be json or pdf")
            return

        directory.mkdir(parents=True, exist_ok=True)
        files = sorted(
            [p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in suffixes]
        )
        self.send_json({"files": files})

    def handle_json_file(self, path: str) -> None:
        name = os.path.basename(path.replace("/api/json/", "", 1))
        target = (RESULTS_DIR / name).resolve()
        if target.parent != RESULTS_DIR.resolve() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "JSON file not found")
            return

        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.send_json(data)

    def handle_pdf_file(self, path: str) -> None:
        name = os.path.basename(path.replace("/api/pdf/", "", 1))
        target = (PDF_DIR / name).resolve()
        if target.parent != PDF_DIR.resolve() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "PDF file not found")
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(target.stat().st_size))
        self.end_headers()
        with open(target, "rb") as f:
            self.wfile.write(f.read())

    def send_json(self, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), PageIndexHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
