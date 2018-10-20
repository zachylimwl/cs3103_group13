import socket
import threading

from constants import *


class P2pServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((P2P_SERVER_HOST, P2P_SERVER_PORT))

    def listen_for_new_peer(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_peer, args=(client,)).start()

    def listen_to_peer(self, client):
        while True:
            try:
                data = client.recv(RECEIVE_SIZE_BYTE)
                if data:
                    print(data.decode())
            except Exception as e:
                client.close()
                print(e)
