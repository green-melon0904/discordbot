import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _Health(BaseHTTPRequestHandler):
    """Render のスリープ防止用：監視リクエストに 200 OK を返す最小ハンドラ。"""

    def do_GET(self):
        self._send_ok(include_body=True)

    def do_HEAD(self):
        self._send_ok(include_body=False)

    def _send_ok(self, include_body: bool):
        body = b"OK\n"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def log_message(self, *args):  # アクセスログを抑制
        pass


def keep_alive():
    """Render が渡す $PORT（ローカルは8080）で待ち受けるWebサーバーを
    デーモンスレッドで起動する。これにより Render に Web Service として
    認識され、UptimeRobot 等の定期ping でスリープを防げる。"""
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _Health)
    threading.Thread(target=server.serve_forever, daemon=True).start()
