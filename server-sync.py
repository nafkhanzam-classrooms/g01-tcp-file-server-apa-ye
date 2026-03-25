import socket
import os

HOST = '0.0.0.0'
PORT = 5000
BASE_DIR = 'server_files'

os.makedirs(BASE_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"[SYNC] Server running on {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"[SYNC] Connected: {addr}")

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break

        if data.startswith('/list'):
            files = os.listdir(BASE_DIR)
            conn.send(("\n".join(files) + "\n").encode())

        elif data.startswith('/upload'):
            _, filename = data.split()
            filepath = os.path.join(BASE_DIR, filename)

            with open(filepath, 'wb') as f:
                while True:
                    chunk = conn.recv(1024)
                    if chunk.endswith(b'EOF'):
                        f.write(chunk[:-3])
                        break
                    f.write(chunk)

            conn.send(b"Upload done\n")

        elif data.startswith('/download'):
            _, filename = data.split()
            filepath = os.path.join(BASE_DIR, filename)

            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        conn.send(chunk)
                conn.send(b'EOF')
            else:
                conn.send(b'File not found\n')

    print(f"[SYNC] Disconnected: {addr}")
    conn.close()