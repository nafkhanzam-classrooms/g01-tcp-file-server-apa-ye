[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Farrel Prastita Ramadhan               |    5025241219        |   D        |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

### Code server-sync.py :

```
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
```

- Deskripsi

Program ini adalah server TCP sederhana yang bekerja secara synchronous atau blocking. Server hanya dapat melayani satu client dalam satu waktu, sehingga jika ada client lain yang mencoba terhubung, maka harus menunggu sampai client sebelumnya selesai.

- Cara Kerja

Server akan membuat socket, lalu menunggu koneksi dari client. Setelah client terhubung, server akan membaca perintah yang dikirim dan memprosesnya satu per satu. Selama proses ini berlangsung, server tidak dapat menerima koneksi baru.

```
conn, addr = server.accept()
```

- Penjelasan:

Baris ini digunakan untuk menerima koneksi dari client. Program akan berhenti sementara sampai ada client yang terhubung.

```
data = conn.recv(1024).decode()
```

- Penjelasan:

Server membaca data yang dikirim oleh client dalam bentuk byte, kemudian diubah menjadi string agar bisa diproses.

```
with open(filepath, 'rb') as f:
    while True:
        chunk = f.read(1024)
        if not chunk:
            break
        conn.send(chunk)
conn.send(b'EOF')
```

- Penjelasan:
Server membaca file sedikit demi sedikit lalu mengirimkannya ke client. Setelah selesai, server mengirim tanda EOF sebagai penanda akhir file.

### Code server-thread.py :

```
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
```

- Deskripsi

Program ini adalah server TCP yang menggunakan multithreading. Setiap client yang terhubung akan ditangani oleh thread yang berbeda sehingga server dapat melayani banyak client secara bersamaan.

- Cara Kerja

Ketika ada client yang terhubung, server akan membuat thread baru. Thread tersebut akan menangani semua komunikasi dengan client tersebut, sehingga server utama tetap bisa menerima client lain.

```
threading.Thread(target=handle_client, args=(conn, addr)).start()
```

- Penjelasan:

Setiap client akan dijalankan dalam thread terpisah, sehingga bisa berjalan secara paralel.

```
def handle_client(conn, addr):
```

- Penjelasan:

Fungsi ini berisi semua logika komunikasi antara server dan client, seperti menerima command dan mengirim response.

```
def broadcast(msg):
    for c in clients:
        c.send(msg.encode())
```
Penjelasan:
Digunakan untuk mengirim pesan ke semua client, misalnya saat ada file yang berhasil diupload.

### Code server-select.py :

```
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
```

- Deskripsi

Program ini menggunakan metode select untuk menangani banyak koneksi dalam satu thread. Pendekatan ini disebut I O multiplexing.

- Cara Kerja

Server menyimpan semua socket dalam sebuah list. Kemudian fungsi select digunakan untuk mengecek socket mana yang siap digunakan. Server hanya akan membaca socket yang aktif, sehingga lebih efisien dibanding blocking.

```
read_socks, _, _ = select.select(sockets, [], [])
```

- Penjelasan:

Fungsi ini akan mengembalikan daftar socket yang siap dibaca. Server hanya akan memproses socket tersebut.

```
sockets.append(conn)
```

- Penjelasan:

Setiap client yang terhubung akan dimasukkan ke dalam list agar bisa dimonitor oleh select.

### Code server-poll.py :

```
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
```

- Deskripsi

Program ini menggunakan metode poll yang merupakan pengembangan dari select. Poll lebih efisien untuk jumlah koneksi yang besar.

- Cara Kerja

Server mendaftarkan socket ke dalam poller. Ketika ada aktivitas pada socket, poll akan memberikan notifikasi sehingga server dapat langsung memprosesnya.

```
poller = select.poll()
```

- Penjelasan:

Digunakan untuk membuat objek poll yang akan memonitor banyak socket.

```
poller.register(server, select.POLLIN)
```

- Penjelasan:

Socket server didaftarkan agar poll bisa mendeteksi jika ada koneksi masuk.

```
events = poller.poll()
```

- Penjelasan:

Poll akan mengembalikan daftar socket yang memiliki aktivitas, sehingga server hanya memproses socket tersebut.

### Code client.py :

```
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
```

- Deskripsi

Program ini adalah client yang digunakan untuk berkomunikasi dengan server. Client dapat mengirim perintah dan menerima response dari server.

- Cara Kerja

Client akan terhubung ke server, kemudian pengguna dapat memasukkan command. Command tersebut dikirim ke server, lalu client akan menampilkan hasilnya.

```
client.connect((HOST, PORT))
```

- Penjelasan:

Client membuat koneksi ke server menggunakan alamat dan port yang sudah ditentukan.

```
with open(filename, 'rb') as f:
    while True:
        chunk = f.read(1024)
        if not chunk:
            break
        client.send(chunk)
client.send(b'EOF')
```

- Penjelasan:

File dibaca sedikit demi sedikit lalu dikirim ke server. Setelah selesai, dikirim tanda EOF.

```
chunk = client.recv(1024)
```

- Penjelasan:

Client menerima data dari server secara bertahap sampai menemukan tanda EOF.
## Screenshot Hasil
