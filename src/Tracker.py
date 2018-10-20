import socket
import threading

from constants import *


class Tracker:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((TRACKER_HOST, TRACKER_PORT))

    def listen_for_new_client(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_client, args=(client,)).start()

    def listen_to_client(self, client):
        while True:
            try:
                data = client.recv(RECEIVE_SIZE_BYTE)
                if data:
                    print(data.decode())
            except Exception as e:
                client.close()
                print(e)


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
