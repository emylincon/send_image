import RPi.GPIO as GPIO
import os
from threading import Thread
import time
import glob
from drawnow import *
from matplotlib import pyplot as plt
import psutil
import base64
import codecs as c
import socket


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

algo = psutil.Process()
cel_x = []
fer_x = []
memory = []
_cpu = []
prev_t = 0            # variable for cpu util
style = ['g--^', 'r:o', 'b-.s', 'm--*', 'k-.>', 'c-.s']

fig = plt.figure()
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
save = 0
file_name = 'iot.png'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        cel_x.append(temp_c)
        fer_x.append(temp_f)


def calculate_mov_avg(a1):
    ma1 = []  # moving average list
    avg1 = 0  # moving average point-wise
    count = 0
    for i in range(len(a1)):
        count += 1
        avg1 = ((count - 1) * avg1 + a1[i]) / count
        ma1.append(avg1)  # cumulative average formula
        # μ_n=((n-1) μ_(n-1)  + x_n)/n
    return ma1


def plot_normal_graph():
    x = list(range(len(calculate_mov_avg(cel_x))))
    ax1.grid(True)
    # ax1.plot(cel_x, linewidth=2, label='Temp C')
    ax1.plot(x, calculate_mov_avg(cel_x), 'm--*', linewidth=2, label='Temp in C')

    ax1.set_ylabel('Temperature')
    ax1.set_xlabel('Time (seconds)')
    # ax1.fill_between(x, calculate_mov_avg(cel_x), 0, alpha=0.5, color='m')
    ax1.legend()
    ax1.set_title('Temperature in Celsius')
    plt.subplot(ax1)

    # plt.show()


def plot_moving_graph():
    x = list(range(len(fer_x)))
    ax2.grid(True)
    # ax2.plot(fer_x, 'g--^', linewidth=2, label='Temp in F')
    # ax2.fill_between(x, fer_x, 0, alpha=0.5, color='g')
    ax2.plot(calculate_mov_avg(fer_x), 'g-->', linewidth=2, label='Temp in F')

    # ax2.set_ylabel('Temperature')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_title('Temperature in Fahrenheit')
    ax2.legend()
    plt.subplot(ax2)


def plot_memory():
    global memory

    memory.append(round(algo.memory_percent(), 4))

    ax3.grid(True)
    ax3.plot(list(range(len(calculate_mov_avg(memory)))), calculate_mov_avg(memory), linewidth=2, label='Memory',
             color='m')
    # ax3.set_title('Moving Memory Utilization')
    ax3.set_ylabel('Moving Memory')
    ax3.set_xlabel('Time (seconds)')
    # cleaax3.set_title('Memory Utilization')
    ax3.fill_between(list(range(len(calculate_mov_avg(memory)))), calculate_mov_avg(memory), 0, alpha=0.3, color='m')
    ax3.legend()
    plt.subplot(ax3)


def plot_cpu():
    global prev_t

    # get cpu
    next_t = psutil.cpu_percent(percpu=False)
    delta = abs(prev_t - next_t)
    prev_t = next_t
    _cpu.append(round(delta, 4))
    ax4.grid(True)
    ax4.plot(list(range(len(calculate_mov_avg(_cpu)))), calculate_mov_avg(_cpu), linewidth=2, label='CPU')
    ax4.set_xlabel('Time (seconds)')
    ax4.fill_between(list(range(len(calculate_mov_avg(_cpu)))), calculate_mov_avg(_cpu), 0, alpha=0.2)
    ax4.legend()
    plt.subplot(ax4)


def delete_previous(path):
    try:
        os.remove(path)
    except Exception as e:
        pass


def plot_graphs():
    global save

    plot_normal_graph()
    plot_moving_graph()
    plot_memory()
    plot_cpu()
    plt.subplots_adjust(wspace=0.3, hspace=0.2)
    if save == 1:
        plt.savefig(file_name)
        save = 0


def graph_temp():
    while True:
        try:
            read_temp()
            drawnow(plot_graphs)
            time.sleep(.6)
        except KeyboardInterrupt:
            print("\nProgramme Terminated\n")
            break


def fin1(file):
    with open(file, "rb") as imageFile:
        s = base64.b64encode(imageFile.read())
        return s


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def unicast_call():
    global save

    host = '0.0.0.0'
    port = 65001        # Port to listen on (non-privileged ports are > 1023)

    print('Server IP: {}'.format(ip_address()))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            while True:
                s.listen()  #
                conn, addr = s.accept()
                with conn:
                    print('Client Connected: ', addr)
                    while True:
                        data = conn.recv(1024)
                        msg = data.decode()
                        if msg == 'send image':
                            try:
                                delete_previous(path=file_name)
                                save = 1
                                time.sleep(2)
                                send = fin1(file_name)
                                length = str(len(send)).encode()
                                conn.sendall(length)
                                conn.sendall(send)
                            except Exception as e:
                                print(e)
                                conn.close()
                                break
                        elif msg == 'light on':
                            GPIO.output(17, True)
                            print("light on")
                        elif msg == 'light off':
                            GPIO.output(17, False)
                            print('light off')
                        elif msg.lower() == 'exit':
                            print('Client Disconnected')
                            conn.close()
                            break
                        else:
                            print(msg)
                            conn.close()
                            break
                        
    except Exception as e:
        print(e)


def main():
    try:
        h1 = Thread(target=unicast_call)
        h1.start()
        graph_temp()
    except KeyboardInterrupt:
        os.system('kill -9 {}'.format(os.getpid()))
        print('Programme Terminated')


if __name__ == "__main__":
    main()

