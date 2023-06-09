import os
import socket
import io
import sys
import time

HALF_SIZE = (os.path.getsize("file.txt") // 2)  # Half size of the file
SERVER_ADDR = ("127.0.0.1", 9999)  
BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE # 8192
AUTH = f"{(8039) ^ (7214)}".encode()  # xor between our ids
FIRST_HALF_FILE = "first_half.txt" 
SECOND_HALF_FILE = "second_half.txt"
FILE = "file.txt"
OK_MSG = b"Yuval&Ron"
FAIL = 1
AGAIN = b"again"
BYE = b"bye"


def divide_file(file):
    """
    TODO The function dividing the file into 2 halfs
    """
    try:
        first = file.read(HALF_SIZE)
        file.seek(HALF_SIZE)
        second = file.read()

        with open(FIRST_HALF_FILE, "wb") as f1:
           f1.write(first)

        with open(SECOND_HALF_FILE, "wb") as f2:
            f2.write(second)
    except Exception as e:
        print(e)
        sys.exit(FAIL)


def main():

    try:
        with open(FILE, "rb") as file:
            divide_file(file)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as client_sock:
            client_sock.connect(SERVER_ADDR)
            while True:
                client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, b"cubic")

                with open(FIRST_HALF_FILE, "rb") as file:
                    while True:
                        data = file.read(BUFFER_SIZE)
                        if not data:
                            break
                        client_sock.sendall(data)
                print("First half has been sent.")

                client_sock.sendall(OK_MSG)

                auth = client_sock.recv(BUFFER_SIZE)
                if auth != AUTH:
                    print("Authintication doesnt match.\nExiting...")
                    sys.exit(FAIL)
                print("Authentication match.")

                client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, b"reno")

                with open(SECOND_HALF_FILE, "rb") as file:
                    while True:
                        data = file.read(BUFFER_SIZE)
                        if not data:
                            break
                        client_sock.sendall(data)
                print("Second file has been sent.")

                client_sock.sendall(OK_MSG)

                desicion = input("Send file again? (y/n)")
                if desicion == "y" or desicion == "Y":
                    client_sock.sendall(AGAIN)
                    continue
                elif desicion == "n" or desicion == "N":
                    print("Exiting...")
                    client_sock.sendall(BYE)
                    client_sock.shutdown(socket.SHUT_RDWR)
                    break
    except Exception as e:
        print(e)
        sys.exit(FAIL)


if __name__ == "__main__":
    main()