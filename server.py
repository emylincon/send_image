import socket
import os


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


print("**********************************")
print(ip_address())
print("**********************************")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip_address(), 5005))
server_socket.listen(5)
client_socket, address = server_socket.accept()
print("Conencted to - ",address,"\n")
while (1):
    choice = client_socket.recv(1024)
    choice = int(choice)
    if(choice == 1):
        data = client_socket.recv(1024)
        print("The following data was received - ",data)
        print("Opening file - ",data)
        fp = open(data,'r')
        strng = fp.read()
        size = os.path.getsize(data)
        size = str(size)
        client_socket.send(size.encode())
        client_socket.send (strng.encode())
        #client_socket.close()

    if (choice == 2 or choice == 3):
        data = client_socket.recv(1024)
        print("The following data was received - ",data)
        print("Opening file - ",data)
        img = open(data,'r')
        while True:
            strng = img.readline(512)
            if not strng:
                break
            client_socket.send(strng.encode())
        img.close()
        print("Data sent successfully")
        exit()
        #data = 'viewnior '+data
        #os.system(data)