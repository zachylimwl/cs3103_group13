import socket
import threading
from threading import Lock
import json

from constants import *


class Tracker:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((TRACKER_HOST, TRACKER_PORT))
        self.lock = Lock()
        self.file_details = {}
        self.file_owners = {} #for query 2: asking for files owners
        self.chunk_details = {}
        self.entries = {}


    def handle_advertise_message(self, payload):
        peer_id = payload[PAYLOAD_PEER_ID_KEY]

        for file_from_peer in payload[PAYLOAD_LIST_OF_FILES_KEY]:
            file_name = file_from_peer[PAYLOAD_FILENAME_KEY]
            if file_name not in self.entries:
                self.entries[file_name] = {}
                self.entries[file_name][PAYLOAD_NUMBER_OF_CHUNKS_KEY] = file_from_peer[PAYLOAD_NUMBER_OF_CHUNKS_KEY]
            if file_name not in self.file_owners:
                #create new list for that peer_id
                self.file_owners[file_name] = [peer_id]
            elif peer_id not in self.file_owners[file_name]:
                self.file_owners[file_name].append(peer_id)

        for chunks_of_file_from_peer in payload[PAYLOAD_LIST_OF_CHUNKS_KEY]:
            file_name = chunks_of_file_from_peer[PAYLOAD_FILENAME_KEY]
            #for every chunk of the file
            for ch in chunks_of_file_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]:
                chunk_num = ch[0]
                checksum = ch[1]
                print(chunk_num + " " + checksum)
                self.entries[file_name][chunk_num] = checksum

                #if chunk number not in the entries  
                # if chunk_num not in self.entries[file_name]:
                #     print("yes")
                    # self.entries[file_name][chunk_num] = {}
                    # self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY] = []
                    # self.entries[file_name][chunk_num][PAYLOAD_CHECKSUM_KEY] = checksum
                #     self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                # #if the chunk's file is inside, but the peer is not inside
                # elif peer_id not in self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY]:
                #     self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                # #else:



        return peer_id

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
                    #print(data.decode())
                    payload = json.loads(data)          
                    if payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_ADVERTISE:
                        self.lock.acquire()
                        peer_id = self.handle_advertise_message(payload)
                        self.lock.release()
                        #print(self.entries)
                        #if tcp need to ack back ??? then ack using the peer_id (source ip and port all there)
                    #create if statements for other types of messages here
                    #if payload[MESSAGE_TYPE] == other request type:
            except Exception as e:
                client.close()
                print(e)


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
