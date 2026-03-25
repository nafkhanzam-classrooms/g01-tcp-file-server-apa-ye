import socket
import select
import os

HOST = '0.0.0.0'
PORT = 5003
BASE_DIR = 'server_files'

os.makedirs(BASE_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
server.setblocking(False)

poller = select.poll()
poller.register(server, select.POLLIN)

fd_to_socket = {server.fileno(): server}

print(f"[POLL] Server running on {HOST}:{PORT}")

while True:
    events = poller.poll()

    for fd, flag in events:
        sock = fd_to_socket[fd]

        if sock == server:
            conn, addr = server.accept()
            conn.setblocking(False)

            fd_to_socket[conn.fileno()] = conn
            poller.register(conn, select.POLLIN)

            print(f"[POLL] Connected: {addr}")

        elif flag & select.POLLIN:
            data = sock.recv(1024)

            if not data:
                poller.unregister(fd)
                del fd_to_socket[fd]
                sock.close()
                continue

            if data.decode().startswith('/list'):
                files = os.listdir(BASE_DIR)
                sock.send(("\n".join(files) + "\n").encode())