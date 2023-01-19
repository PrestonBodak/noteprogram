import os
import shutil
import pickle
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    //sock.bind(("INSERT SERVER IP ADDRESS HERE", 4454))

    while True:
        print("Awaiting connection...")
        sock.listen()
        conn, address = sock.accept()
        print("Connection made!")
        fileName = conn.recv(1024).decode()
        fileName = fileName[:-1].rindex("\\")
        print(fileName)
        data = pickle.load(sock.recv(1024))
        file = open(fileName, "w")
        file.write(bytearray(data))
        file.close()
