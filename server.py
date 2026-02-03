#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from pathlib import Path

PORT = 8080
BASE = Path(__file__).parent
MESH_DIR = BASE / "game_data" / "meshes"
TEX_DIR = BASE / "game_data" / "textures"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(BASE), **kw)

    def do_GET(self):
        if self.path == "/list_raw_hlod":
            files = sorted(f for f in os.listdir(MESH_DIR)
                           if f.endswith('.obj')) if MESH_DIR.exists() else []
            return self._json(files)
        if self.path.startswith("/raw_hlod/"):
            return self._file(MESH_DIR / self.path[10:], "model/obj")
        if self.path.startswith("/textures/"):
            return self._file(TEX_DIR / self.path[10:], "image/png")
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _file(self, path, ctype):
        if path.exists():
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(path.read_bytes())
        else:
            self.send_error(404)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


if __name__ == "__main__":
    m = len(list(MESH_DIR.glob("*.obj"))) if MESH_DIR.exists() else 0
    t = len(list(TEX_DIR.glob("*.png"))) if TEX_DIR.exists() else 0
    print(f"http://localhost:{PORT}/ | Meshes: {m} | Textures: {t}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
