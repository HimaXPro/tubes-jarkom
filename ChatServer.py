import socket
import threading

class ChatServer:
    def __init__(self, host='127.0.0.1', port=6789):
        # Inisialisasi server dengan host dan port
        self.host = host
        self.port = port
        # Membuat socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # List untuk menyimpan koneksi client yang terhubung
        self.clients = []
        # List untuk menyimpan pesan chat
        self.messages = []

    def start(self):
        # Mengikat socket ke host dan port
        self.server_socket.bind((self.host, self.port))
        # Mendengarkan koneksi masuk, maksimal 5 antrian
        self.server_socket.listen(5)
        print(f"Server dimulai di {self.host}:{self.port}")
        while True:
            # Menerima koneksi client baru
            client_socket, addr = self.server_socket.accept()
            print(f"Koneksi dari {addr}")
            # Membuat thread baru untuk menangani client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            # Menambahkan socket client ke list clients
            self.clients.append(client_socket)

    def handle_client(self, client_socket):
        try:
            while True:
                # Menerima data dari client
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    # Jika tidak ada data, berarti client putus koneksi
                    break
                # Memproses request yang diterima
                response = self.process_request(data)
                if response:
                    # Mengirim response ke client
                    client_socket.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            # Menangani client yang putus koneksi secara tiba-tiba
            pass
        finally:
            # Menutup socket client dan menghapus dari list clients
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)

    def process_request(self, data):
        # Memisahkan request menjadi baris-baris
        lines = data.split('\r\n')
        if len(lines) < 1:
            # Request tidak valid jika tidak ada baris
            return "HTTP/1.1 400 Bad Request\r\n\r\n"
        # Mengambil baris pertama request (misal: "POST /chat HTTP/1.1")
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) < 2:
            # Request tidak valid jika baris pertama tidak lengkap
            return "HTTP/1.1 400 Bad Request\r\n\r\n"
        method = parts[0]
        if method == 'POST':
            # Menangani metode POST untuk menerima pesan
            try:
                # Mencari baris kosong yang memisahkan header dan body
                empty_line_index = lines.index('')
                # Mengambil isi pesan dari body
                body = '\r\n'.join(lines[empty_line_index+1:])
                # Menyimpan pesan
                self.messages.append(body)
                # Mengirim response sukses
                return "HTTP/1.1 200 OK\r\n\r\nPesan diterima"
            except ValueError:
                # Jika tidak ada baris kosong, request tidak valid
                return "HTTP/1.1 400 Bad Request\r\n\r\n"
        elif method == 'GET':
            # Menangani metode GET untuk mengirim semua pesan
            body = '\n'.join(self.messages)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                "\r\n"
                f"{body}"
            )
            return response
        else:
            # Metode selain POST dan GET tidak diizinkan
            return "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

if __name__ == "__main__":
    # Membuat dan menjalankan server chat
    server = ChatServer()
    server.start()
