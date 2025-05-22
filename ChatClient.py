import socket

class ChatClient:
    def __init__(self, host='127.0.0.1', port=6789):
        # Inisialisasi client dengan host dan port server
        self.host = host
        self.port = port
        # Membuat socket TCP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # Menghubungkan ke server
        self.client_socket.connect((self.host, self.port))

    def send_post(self, message):
        # Membuat request POST dengan format HTTP-like
        request = (
            "POST /chat HTTP/1.1\r\n"
            f"Content-Length: {len(message.encode('utf-8'))}\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            f"{message}"
        )
        # Mengirim request ke server
        self.client_socket.sendall(request.encode('utf-8'))
        # Menerima response dari server
        response = self.receive_response()
        print("Response dari server:", response)

    def send_get(self):
        # Membuat request GET dengan format HTTP-like
        request = (
            "GET /chat HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            "\r\n"
        )
        # Mengirim request ke server
        self.client_socket.sendall(request.encode('utf-8'))
        # Menerima response dari server
        response = self.receive_response()
        print("Pesan dari server:\n", response)

    def receive_response(self):
        # Menerima response dari server secara bertahap
        response = b""
        while True:
            part = self.client_socket.recv(1024)
            response += part
            if len(part) < 1024:
                break
        # Mengembalikan response dalam bentuk string
        return response.decode('utf-8')

    def close(self):
        # Menutup koneksi socket
        self.client_socket.close()

if __name__ == "__main__":
    # Membuat instance client dan menghubungkan ke server
    client = ChatClient()
    client.connect()
    print("Terhubung ke server chat.")
    try:
        while True:
            # Meminta input perintah dari user
            command = input("Masukkan perintah (POST untuk kirim, GET untuk terima, QUIT untuk keluar): ").strip().upper()
            if command == 'POST':
                # Mengirim pesan ke server
                message = input("Masukkan pesan yang akan dikirim: ")
                client.send_post(message)
            elif command == 'GET':
                # Meminta pesan dari server
                client.send_get()
            elif command == 'QUIT':
                # Keluar dari aplikasi
                break
            else:
                print("Perintah tidak dikenal.")
    finally:
        # Menutup koneksi saat keluar
        client.close()
        print("Terputus dari server.")
