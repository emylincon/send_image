import base64
import codecs as c

import socket
import os


def fin2(barr, dfile):  # this returns a image
    fh = open(dfile, "wb")
    # fh.write(barr.decode('base64'))
    fh.write(c.decode(obj=barr, encoding='base64'))
    fh.close()


def client():
    host = input('Server IP: ').strip()  # The server's hostname or IP address
    port = 65001  # The port used by the server

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            fname = input('Enter command: ').strip()
            s.sendall(fname.encode())
            data = s.recv(1024)
            l = data.decode()
            data_ = str.encode('')
            while len(data_) < int(l):
                data_ += s.recv(1024)
            fin2(barr=data_, dfile='new.jpg')
            print('File received')
            s.sendall('exit'.encode())
            s.close()

    except KeyboardInterrupt:
        print('Programme Terminated')


def main():
    os.system('clear')
    print("================== Welcome to Client Platform ===================")
    client()


if __name__ == "__main__":
    main()
