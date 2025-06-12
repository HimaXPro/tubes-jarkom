from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
from urllib.parse import urlparse, parse_qs

# Alamat IP dan port dari server chat yang akan menjadi tujuan proxy
CHAT_SERVER_HOST = '127.0.0.1'
CHAT_SERVER_PORT = 6789

class ProxyHandler(BaseHTTPRequestHandler):
    # Menangani metode HTTP OPTIONS (preflight CORS) dari browser
    def do_OPTIONS(self):
        self.send_response(204)  # Tidak mengembalikan konten
        self.send_header("Access-Control-Allow-Origin", "*")  # Izinkan semua domain
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")  # Izinkan metode tertentu
        self.send_header("Access-Control-Allow-Headers", "Content-Type")  # Izinkan header ini dikirim
        self.end_headers()

    # Menangani permintaan GET dari client (biasanya untuk mengambil pesan)
    def do_GET(self):
        # Buat permintaan GET ke server chat
        http_request = "GET /chat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        response = self.communicate_with_socket(http_request)

        # Kirim kembali response ke browser (client)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')  # Izinkan akses lintas asal (CORS)
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    # Menangani permintaan POST dari client (untuk mengirim pesan)
    def do_POST(self):
        # Ambil panjang isi pesan dari header, lalu baca isinya
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            # Parsing JSON dari body
            data = json.loads(body.decode('utf-8'))
            message = data.get('message', '')
        except:
            # Jika JSON tidak valid, kirim error 400
            self.send_error(400, "Invalid JSON")
            return

        # Tambahkan timestamp (jam dan menit) ke pesan
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M')
        formatted = f"[{timestamp}] {message}"

        # Buat permintaan POST ke server chat dalam format HTTP manual
        http_request = (
            "POST /chat HTTP/1.1\r\n"
            f"Content-Length: {len(formatted.encode('utf-8'))}\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            f"{formatted}"
        )

        # Kirim permintaan ke server chat dan dapatkan responsenya
        response = self.communicate_with_socket(http_request)

        # Kirim kembali responsenya ke client
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    # Fungsi untuk berkomunikasi langsung dengan server chat menggunakan socket TCP
    def communicate_with_socket(self, request_text):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Waktu tunggu maksimal 5 detik untuk mencegah hang
            s.connect((CHAT_SERVER_HOST, CHAT_SERVER_PORT))  # Hubungkan ke server chat
            s.sendall(request_text.encode('utf-8'))  # Kirim request ke server chat

            response = b""  # Buffer untuk menyimpan respons
            while True:
                try:
                    part = s.recv(1024)  # Terima sebagian data (maks 1024 byte)
                    if not part:
                        break
                    response += part
                    if len(part) < 1024:
                        break  # Keluar jika data sudah habis
                except socket.timeout:
                    print("Timeout saat menerima data dari server chat")
                    break

        # Ambil hanya bagian isi (body) dari respons HTTP yang diterima
        return response.decode('utf-8').split('\r\n\r\n', 1)[-1]

# Program utama: menjalankan server proxy di port 5000
if __name__ == "__main__":
    server_address = ('', 5000)  # Jalankan di semua IP lokal, port 5000
    httpd = HTTPServer(server_address, ProxyHandler)
    print("Proxy HTTP server berjalan di port 5000...")
    httpd.serve_forever()  # Jalankan server tanpa henti
