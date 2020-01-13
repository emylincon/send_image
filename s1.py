import base64
import codecs as c
#!/usr/bin/env python3

import socket
import os

def fin2(barr, dfile):  #this returns a image
    fh = open(dfile, "wb")
    #fh.write(barr.decode('base64'))
    fh.write(c.decode(obj=barr, encoding='base64'))
    fh.close()


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def unicast_call():
    host = '0.0.0.0'
    port = 65000        # Port to listen on (non-privileged ports are > 1023)

    print('Server IP: {}'.format(ip_address()))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected: ', addr)
                while True:
                    data = conn.recv(1024)
                    fname = data.decode()
                    data = conn.recv(1024)
                    fin2(barr=data, dfile=fname)
                    if data.decode().lower() == 'exit':
                        print('Programme Terminated by Client')
                        break
    except KeyboardInterrupt:
        print('\nProgramme Forcefully Terminated')


def main():
    os.system('clear')
    print('================== Programme Active =====================\n')
    unicast_call()


if __name__ == "__main__":
    main()

