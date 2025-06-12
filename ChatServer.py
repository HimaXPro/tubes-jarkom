import socket
import threading

# Kelas untuk membuat server chat
class ChatServer:
    def __init__(self, host='127.0.0.1', port=6789):
        # Simpan alamat dan port server
        self.host = host
        self.port = port
        # Buat socket TCP (untuk komunikasi jaringan)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Simpan daftar client yang sedang terhubung
        self.clients = []
        # Simpan pesan-pesan chat
        self.messages = []
        # Batas maksimal jumlah pesan yang disimpan
        self.max_messages = 100

    def start(self):
        # Hubungkan socket ke alamat dan port
        self.server_socket.bind((self.host, self.port))
        # Mulai mendengarkan koneksi (maksimal 5 antrean)
        self.server_socket.listen(5)
        print(f"Server berjalan di {self.host}:{self.port}")

        while True:
            # Terima koneksi baru dari client
            client_socket, addr = self.server_socket.accept()
            print(f"Client terhubung dari {addr}")
            # Buat thread baru untuk menangani client tersebut
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.daemon = True  # Thread akan berhenti jika program utama berhenti
            thread.start()
            # Simpan client ke dalam daftar
            self.clients.append(client_socket)

    def handle_client(self, client_socket):
        try:
            while True:
                # Baca data dari client
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    # Jika tidak ada data, client terputus
                    break

                # Proses data permintaan dari client
                response = self.process_request(data)

                if response:
                    # Kirimkan jawaban ke client
                    client_socket.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            # Client keluar mendadak, abaikan
            pass
        finally:
            # Tutup koneksi dan hapus dari daftar client
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)

    def process_request(self, data):
        # Pisahkan permintaan menjadi baris-baris
        lines = data.split('\r\n')

        if len(lines) < 1:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        # Ambil baris pertama (misalnya: POST /chat HTTP/1.1)
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) < 2:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        # Ambil metode yang digunakan (GET atau POST)
        method = parts[0]

        if method == 'POST':
            # Jika client mengirim pesan
            try:
                # Cari baris kosong yang memisahkan header dan body
                kosong = lines.index('')
                # Gabungkan isi body (pesan)
                body = '\r\n'.join(lines[kosong+1:])
                # Simpan pesan ke dalam daftar
                self.messages.append(body)
                # Hapus pesan lama jika melebihi batas
                if len(self.messages) > self.max_messages:
                    self.messages.pop(0)
                return "HTTP/1.1 200 OK\r\n\r\nPesan diterima"
            except ValueError:
                # Format salah (tidak ada baris kosong)
                return "HTTP/1.1 400 Bad Request\r\n\r\n"

        elif method == 'GET':
            # Jika client ingin melihat semua pesan
            isi_pesan = '\n'.join(self.messages)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(isi_pesan.encode('utf-8'))}\r\n"
                "\r\n"
                f"{isi_pesan}"
            )
            return response

        else:
            # Jika metode tidak didukung (bukan GET atau POST)
            return "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

# Jalankan server jika file ini dijalankan langsung
if __name__ == "__main__":
    server = ChatServer()  # Buat server
    server.start()         # Jalankan server
