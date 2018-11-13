import socket
import threading
from threading import Lock
import json
import sys, errno

from constants import *


class Tracker:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((AWS_TRACKER_HOST, TRACKER_PORT))
        self.lock = Lock()
        self.file_details = {}
        self.file_owners = {} #for query 2: asking for files owners
        self.chunk_details = {}
        self.entries = {}
        self.peer_id_list = []


    def handle_advertise_message(self, payload):
        peer_id = payload[PAYLOAD_PEER_ID_KEY]
        peer_id_pub = payload[PAYLOAD_PUBLIC_PEER_ID_KEY]
        peer_id_tuple = (peer_id, peer_id_pub)
        #then change all peer_id to peer_id_tuple
        
        for file_from_peer in payload[PAYLOAD_LIST_OF_FILES_KEY]:
            file_name = file_from_peer[PAYLOAD_FILENAME_KEY]
            if file_name not in self.entries:
                self.entries[file_name] = {}
            if file_name not in self.file_owners:
                #create new list for that peer_id
                self.file_owners[file_name] = [peer_id_tuple]
            elif peer_id_tuple not in self.file_owners[file_name]:
                self.file_owners[file_name].append(peer_id_tuple)

        for chunks_of_file_from_peer in payload[PAYLOAD_LIST_OF_CHUNKS_KEY]:
            fileName = chunks_of_file_from_peer[PAYLOAD_FILENAME_KEY]
            #for every chunk of the file
            for ch in chunks_of_file_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]:
                chunk_num = ch[0]
                checksum = ch[1]

                if fileName not in self.entries:
                    self.entries[fileName] = {}
                #if chunk number not in the entries  
                if chunk_num not in self.entries[fileName]:
                    self.entries[fileName][chunk_num] = {}
                    self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY] = []
                    self.entries[fileName][chunk_num][PAYLOAD_CHECKSUM_KEY] = checksum
                    self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY].append(peer_id_tuple)
                #if the chunk's file is inside, but the peer is not inside
                elif peer_id_tuple not in self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY]:
                    self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY].append(peer_id_tuple)
        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_ADVERTISE_SUCCESS}

        return response
    
    # Creates the list of chunks for a specific file
    # Format:
    # {
    #   MESSAGE_TYPE : TRACKER_RESPONSE_TYPE_SUCCESS_QUERY_CHUNK_LIST
    #   file_name : {
    #                   CHUNK1 : ([PEER_ID_LIST], CHECKSUM),
    #                   CHUNK2 : ([PEER_ID_LIST], CHECKSUM),
    #                   ...  
    #               }
    # }
    def create_chunk_list(self, file_name):
        response = {}
        # Checks if file exists
        if file_name not in self.entries:
            response[MESSAGE_TYPE] = TRACKER_RESPONSE_TYPE_ERROR
            return response
        # Adds chunk list to response if file exist
        else:
            response[MESSAGE_TYPE] = TRACKER_RESPONSE_TYPE_SUCCESS_QUERY_CHUNK_LIST
            response[CHUNK_LIST] = self.entries[file_name]
            return response

    def handle_list_all_available_files_message(self):
        all_available_files = list(self.entries.keys()) if len(self.entries.keys()) else []

        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_LIST_ALL_AVAILABLE_FILES,
                    LIST_OF_FILES: all_available_files}

        return response

    def handle_content_query(self, payload):
        file_name = payload[PAYLOAD_FILENAME_KEY]
        response = {}
        if file_name not in self.entries:
            response[MESSAGE_TYPE] = TRACKER_FILE_NOT_FOUND
            return response
        if not self.file_owners[file_name]:
            response[MESSAGE_TYPE] = TRACKER_PEERS_NOT_FOUND
            return response
        response[MESSAGE_TYPE] = TRACKER_PEERS_AVAILABLE
        return response

    def handle_exit_message(self, payload):
        ext_addr = payload[PAYLOAD_PUBLIC_PEER_ID_KEY]
        int_addr = payload[PAYLOAD_PEER_ID_KEY]
        peer = (int_addr, ext_addr)
        files_to_delete = []
        chunk_to_delete = []

        # Remove peers from system and keep track of which chunks to remove from each files if no peers exists
        for file_name, chunks in self.entries.items():
            for chunk, details in chunks.items():
                if peer in details[LIST_OF_PEERS_KEY]:
                    details[LIST_OF_PEERS_KEY].remove(peer)
                if len(details[LIST_OF_PEERS_KEY]) == 0:
                    chunk_to_delete.append((file_name, chunk))

        # Delete chunks belong to peers that have exited the system
        for item in chunk_to_delete:
            del(self.entries[item[0]][item[1]])

        # Keep track of files that does not have any chunks
        for file_name, chunks in self.entries.items():
            if not chunks:
                files_to_delete.append(file_name)

        # Remove file that does not have any chunks
        for f in files_to_delete:
            del(self.entries[f])

        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_EXIT}

        return response

    def listen_for_new_client(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_client, args=(client,)).start()

    def displayEntries(self):
        print()
        print("CURRENT ENTRIES IN TRACKER...")
        print()
        print(self.entries)

    def listen_to_client(self, client):
        response = {}
        while True:
            try:
                data = client.recv(RECEIVE_SIZE_BYTE)
                if data:
                    payload = json.loads(data)
                    self.lock.acquire()
                    if payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_ADVERTISE:
                        response = self.handle_advertise_message(payload)
                        self.displayEntries()
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_QUERY_CHUNKS:
                        response = self.create_chunk_list(payload[FILE_NAME])
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES:
                        response = self.handle_list_all_available_files_message()
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT:
                        response = self.handle_content_query(payload)
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_EXIT:
                        response = self.handle_exit_message(payload)
                    else:
                        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_ERROR_NO_SUCH_MESSAGE_TYPE}
                    self.lock.release()
                client.sendall(json.dumps(response).encode())
            except Exception as e:
                client.close()
                if e.errno == errno.EPIPE:
                    print("A client has closed its connection.")
                break


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
