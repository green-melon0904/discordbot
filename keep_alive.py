import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Health(BaseHTTPRequestHandler):
    """Render のスリープ防止用：GETに 200 OK を返すだけの最小ハンドラ。"""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):  # アクセスログを抑制
        pass


def keep_alive():
    """Render が渡す $PORT（ローカルは8080）で待ち受けるWebサーバーを
    デーモンスレッドで起動する。これにより Render に Web Service として
    認識され、UptimeRobot 等の定期ping でスリープを防げる。"""
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), _Health)
    threading.Thread(target=server.serve_forever, daemon=True).start()
