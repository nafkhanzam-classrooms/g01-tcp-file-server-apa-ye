import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5001
BASE_DIR = 'server_files'
clients = []

os.makedirs(BASE_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"[THREAD] Server running on {HOST}:{PORT}")

def broadcast(msg):
    for c in clients:
        try:
            c.send((msg + "\n").encode())
        except:
            pass

def handle_client(conn, addr):
    print(f"[THREAD] Connected: {addr}")
    clients.append(conn)

    while True:
        try:
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
                        if b'EOF' in chunk:
                            chunk = chunk.replace(b'EOF', b'')
                            f.write(chunk)
                            break
                        f.write(chunk)

                conn.send(b"Upload done\n")
                broadcast(f"[SERVER] {filename} uploaded")

            elif data.startswith('/download'):
                _, filename = data.split()
                filepath = os.path.join(BASE_DIR, filename)

                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            conn.sendall(chunk)

                    conn.sendall(b'EOF')
                else:
                    conn.sendall(b'File not found')

        except:
            break

    print(f"[THREAD] Disconnected: {addr}")
    clients.remove(conn)
    conn.close()

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()