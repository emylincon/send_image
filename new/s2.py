import base64
import codecs as c
import socket
import os


def fin1(file):
    with open(file, "rb") as imageFile:
        s = base64.b64encode(imageFile.read())
        return s


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def unicast_call():
    host = '0.0.0.0'
    port = 65001        # Port to listen on (non-privileged ports are > 1023)

    print('Server IP: {}'.format(ip_address()))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected: ', addr)
                    while True:
                        data = conn.recv(1024)
                        msg = data.decode()
                        if msg == 'send image':
                            fname = 'img.jpg'
                            send = fin1(fname)
                            length = str(len(send)).encode()
                            conn.sendall(length)
                            conn.sendall(send)

                        elif msg.lower() == 'exit':
                            print('Programme Terminated by Client')
                            conn.close()
                            break
    except Exception as e:
        print(e)


def main():
    os.system('clear')
    print('================== Programme Active =====================\n')
    unicast_call()


if __name__ == "__main__":
    main()

