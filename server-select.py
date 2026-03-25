import socket
import select
import os

HOST = '0.0.0.0'
PORT = 5002
BASE_DIR = 'server_files'

os.makedirs(BASE_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
server.setblocking(False)

sockets = [server]

print(f"[SELECT] Server running on {HOST}:{PORT}")

while True:
    read_socks, _, _ = select.select(sockets, [], [])

    for sock in read_socks:
        if sock == server:
            conn, addr = server.accept()
            conn.setblocking(False)
            sockets.append(conn)
            print(f"[SELECT] Connected: {addr}")

        else:
            try:
                data = sock.recv(1024).decode()

                if not data:
                    sockets.remove(sock)
                    sock.close()
                    continue

                if data.startswith('/list'):
                    files = os.listdir(BASE_DIR)
                    sock.send(("\n".join(files) + "\n").encode())

            except:
                sockets.remove(sock)
                sock.close()