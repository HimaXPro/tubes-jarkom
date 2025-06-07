from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
from urllib.parse import urlparse, parse_qs

# Host dan port server chat yang akan dihubungi proxy
CHAT_SERVER_HOST = '127.0.0.1'
CHAT_SERVER_PORT = 6789

class ProxyHandler(BaseHTTPRequestHandler):
    # Menangani metode OPTIONS untuk CORS preflight
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # Menangani metode GET, meneruskan request ke server chat melalui socket
    def do_GET(self):
        http_request = "GET /chat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        response = self.communicate_with_socket(http_request)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    # Menangani metode POST, menerima pesan dari client dan meneruskannya ke server chat
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
            message = data.get('message', '')
        except:
            self.send_error(400, "Invalid JSON")
            return

        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M')
        formatted = f"[{timestamp}] {message}"

        http_request = (
            "POST /chat HTTP/1.1\r\n"
            f"Content-Length: {len(formatted.encode('utf-8'))}\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            f"{formatted}"
        )

        response = self.communicate_with_socket(http_request)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    # Fungsi untuk berkomunikasi dengan server chat melalui socket TCP
    def communicate_with_socket(self, request_text):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Set timeout 5 detik untuk menghindari koneksi menggantung
            s.connect((CHAT_SERVER_HOST, CHAT_SERVER_PORT))
            s.sendall(request_text.encode('utf-8'))
            response = b""
            while True:
                try:
                    part = s.recv(1024)
                    if not part:
                        break
                    response += part
                    if len(part) < 1024:
                        break
                except socket.timeout:
                    print("Timeout saat menerima data dari server chat")
                    break
        # Mengembalikan isi body response HTTP dari server chat
        return response.decode('utf-8').split('\r\n\r\n', 1)[-1]

if __name__ == "__main__":
    # Menjalankan proxy HTTP server pada port 5000
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, ProxyHandler)
    print("Proxy HTTP server berjalan di port 5000...")
    httpd.serve_forever()
