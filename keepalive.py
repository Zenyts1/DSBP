import socket


def keepalive(sock):
    host = socket.gethostname()
    port = 5000
    server = socket.socket()
    server.bind((host, port))
    while True:
        server.listen()
        conn, addr = server.accept()