import socket
import os

HOST = '127.0.0.1'
PORT = 5002

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Connected to server")

while True:
    cmd = input("> ")

    if cmd.startswith('/upload'):
        parts = cmd.split()
        if len(parts) != 2:
            print("Format: /upload filename")
            continue

        filename = parts[1]

        if os.path.exists(filename):
            client.send(cmd.encode())

            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client.send(chunk)

            client.send(b'EOF')
            print(client.recv(1024).decode())
        else:
            print("File not found")

    elif cmd.startswith('/download'):
        parts = cmd.split()
        if len(parts) != 2:
            print("Format: /download filename")
            continue

        filename = parts[1]
        client.send(cmd.encode())

        with open(filename, 'wb') as f:
            while True:
                chunk = client.recv(1024)

                if chunk.startswith(b'File not found'):
                    print(chunk.decode())
                    break

                if b'EOF' in chunk:
                    chunk = chunk.replace(b'EOF', b'')
                    f.write(chunk)
                    break

                f.write(chunk)

        print("Download done")

    else:
        client.send(cmd.encode())
        print(client.recv(4096).decode())