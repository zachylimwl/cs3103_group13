import json
import os
import socket
import threading

from constants import *
from FileUtilities import *

class P2pServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((P2P_SERVER_HOST, P2P_SERVER_PORT))
        self.directory = os.getcwd()

    def listen_for_new_peer(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_peer, args=(client,)).start()

    # Receiving request from other peers to send file
    def listen_to_peer(self, client):
        while True:
            data = json.loads(client.recv(RECEIVE_SIZE_BYTE))
            if data[MESSAGE_TYPE] == PEER_REQUEST_TYPE_CHUNK_DOWNLOAD:
                print("Peer Connected to P2PServer, sending requested file")
                file_name = data[FILE_NAME]
                chunk_number = data[PEER_REQUEST_TYPE_CHUNK_NUMBER]
                chunk_bytes = self.get_file_chunk_to_send(file_name, chunk_number)
                client.sendall(chunk_bytes)
                client.close()
                break
            
    # Get file_chunk from dir to send to peer
    def get_file_chunk_to_send(self, file_name, chunk_number):
        chunk_bytes = None
        # File exists, read part of the chunk to send
        if does_file_exist(file_name, self.directory):
            target_file = open_file(file_name, self.directory)
            target_file.seek((int(chunk_number) - 1) * CHUNK_SIZE)
            chunk_bytes = target_file.read(CHUNK_SIZE)
        # Chunk exist, sends whole chunk
        else:
            target_chunk = open_file(create_chunk_file_name(file_name, chunk_number), self.directory)
            chunk_bytes = target_chunk.read(CHUNK_SIZE)
        return chunk_bytes

