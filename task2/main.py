import subprocess
import socket
import struct
import random
import time
import mmap
import sys

EXE_NAME = r'C:\Users\surma\OneDrive\Робочий стіл\Super\3\helper\x64\Debug\helper.exe'

def test_pipe():
    num = random.randint(1, 100)
    start = time.perf_counter()

    # Запускаємо C++ процес у режимі 'pipe'
    proc = subprocess.Popen([EXE_NAME, 'pipe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = proc.communicate(input=f"{num}\n")

    end = time.perf_counter()
    print(f"Час обміну через Pipe: {(end - start) * 1000:.4f} мс")

def test_socket():
    num = random.randint(1, 100)
    proc = subprocess.Popen([EXE_NAME, 'socket'])

    start = time.perf_counter()
    s = None
    for _ in range(50):  # до 5 секунд (50 * 0.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 8080))
            break
        except ConnectionRefusedError:
            time.sleep(0.1)
            continue
    else:
        print("Не вдалося підключитися до сокет-сервера")
        proc.terminate()
        return

    s.send(struct.pack('i', num))
    data = s.recv(4)
    s.close()
    end = time.perf_counter()

    proc.wait()  # дочекаємось завершення C++
    print(f"Час обміну через Socket: {(end - start) * 1000:.4f} мс")

def test_shared_memory():
    num = random.randint(1, 100)
    start = time.perf_counter()

    mm = mmap.mmap(-1, 4096, tagname="Local\\MySharedMemBlock", access=mmap.ACCESS_WRITE)
    try:
        mm[0] = 1
        mm[1:5] = struct.pack('i', num)
        mm.flush() 

        # Запускаємо C++ процес, який прочитає ці дані
        proc = subprocess.Popen([EXE_NAME, 'shm'])

        # Чекаємо, поки C++ встановить прапорець підтвердження
        while mm[0] != 2:
            time.sleep(0.001)
    finally:
        mm.close()

    proc.wait()
    end = time.perf_counter()
    print(f"Час обміну через Shared Memory: {(end - start) * 1000:.4f} мс")

if __name__ == "__main__":
    print("ТЕСТУВАННЯ МЕТОДІВ IPC")
    test_pipe()
    test_socket()
    test_shared_memory()