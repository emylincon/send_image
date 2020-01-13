import base64
import codecs as c

import socket
import os


def fin1(file):
    with open(file, "rb") as imageFile:
        s = base64.b64encode(imageFile.read())
        return s


def client():
    host = input('Server IP: ').strip()  # The server's hostname or IP address
    port = 65000        # The port used by the server

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            while True:
                fname = input('Enter filename: ').strip()
                send = fin1(fname)
                length = str(len(send)).encode()
                s.sendall(length)
                s.sendall(send)
                if send.lower() == 'exit':
                    print('Programme Terminated')
                    break
    except KeyboardInterrupt:
        print('Programme Terminated')


def main():
    os.system('clear')
    print("================== Welcome to Client Platform ===================")
    client()


if __name__ == "__main__":
    main()

