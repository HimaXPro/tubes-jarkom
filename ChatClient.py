import socket
from colorama import init, Fore, Style
from datetime import datetime

# Inisialisasi colorama agar output berwarna
init(autoreset=True)

class ChatClient:
    def __init__(self, host='127.0.0.1', port=6789):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))

    def send_post(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request = (
            "POST /chat HTTP/1.1\r\n"
            f"Content-Length: {len(message.encode('utf-8'))}\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            f"{message}"
        )
        self.client_socket.sendall(request.encode('utf-8'))
        response = self.receive_response()
        print(Fore.GREEN + f"[{timestamp}] Response dari server:\n{response}")

    def send_get(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request = (
            "GET /chat HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            "\r\n"
        )
        self.client_socket.sendall(request.encode('utf-8'))
        response = self.receive_response()
        print(Fore.BLUE + f"[{timestamp}] Pesan dari server:\n{response}")

    def receive_response(self):
        response = b""
        while True:
            part = self.client_socket.recv(1024)
            response += part
            if len(part) < 1024:
                break
        return response.decode('utf-8')

    def close(self):
        self.client_socket.close()

if __name__ == "__main__":
    client = ChatClient()
    client.connect()
    print(Fore.YELLOW + "Terhubung ke server chat.")
    try:
        while True:
            # Input perintah - jadi tidak sensitif besar kecil
            command = input("Masukkan perintah (POST untuk kirim, GET untuk terima, QUIT untuk keluar): ").strip().lower()
            if command == 'post':
                message = input("Masukkan pesan yang akan dikirim: ")
                client.send_post(message)
            elif command == 'get':
                client.send_get()
            elif command == 'quit':
                break
            else:
                print(Fore.RED + "Perintah tidak dikenal.")
    finally:
        client.close()
        print(Fore.YELLOW + "Terputus dari server.")
