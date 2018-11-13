import socket
from constants import *
import threading
import json


class TurnServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((AWS_TURN_SERVER_HOST, TURN_PORT))

    def listen_for_new_connection(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_client, args=(client, addr)).start()

    def listen_to_client(self, client, addr):
        relay_transport_address = (AWS_TURN_SERVER_HOST, addr[1])
        self.socket.bind(relay_transport_address)
        message = {RELAYED_TRANSPORT_ADDRESS_KEY: relay_transport_address}
        client.sendall(json.dumps(message).encode())
        while True:
            data = client.recv(RECEIVE_SIZE_BYTE)
            

def main():
    server = TurnServer()
    server.listen_for_new_connection()


main()
