"""
Tiny static server for the Multi Model RAG frontend.

Run:
    python frontend/serve.py
Then open:
    http://127.0.0.1:5500
"""

import http.server
import os
import socketserver

PORT = int(os.environ.get("PORT", 5500))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Frontend running at http://127.0.0.1:{PORT}")
        print("Backend expected at http://127.0.0.1:8000 (FastAPI)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
