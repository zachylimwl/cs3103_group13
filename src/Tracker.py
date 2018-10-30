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
        self.peer_id_list = []


    def handle_advertise_message(self, payload):
        peer_id = payload[PAYLOAD_PEER_ID_KEY]

        for file_from_peer in payload[PAYLOAD_LIST_OF_FILES_KEY]:
            file_name = file_from_peer[PAYLOAD_FILENAME_KEY]
            if file_name not in self.entries:
                self.entries[file_name] = {}
                # Temporary removal for easier iteration (I think its not really needed /Sherina)
                # self.entries[file_name][PAYLOAD_NUMBER_OF_CHUNKS_KEY] = file_from_peer[PAYLOAD_NUMBER_OF_CHUNKS_KEY]
            if file_name not in self.file_owners:
                #create new list for that peer_id
                self.file_owners[file_name] = [peer_id]
            elif peer_id not in self.file_owners[file_name]:
                self.file_owners[file_name].append(peer_id)

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
                    self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                #if the chunk's file is inside, but the peer is not inside
                elif peer_id not in self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY]:
                    self.entries[fileName][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                #else:
                # self.chunk_details[file_name][peer_id] = list(set(self.chunk_details[file_name][peer_id] + chunk_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]))

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
            response[file_name] = self.entries[file_name]
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

    def handle_exit_message(self, addr):
        ip = addr[0]
        files_to_delete = []

        for file_name, chunks in self.entries.items():
            for chunk, details in chunks.items():
                if chunk == PAYLOAD_NUMBER_OF_CHUNKS_KEY:
                    continue
                details[LIST_OF_PEERS_KEY].remove(ip)
                if len(details[LIST_OF_PEERS_KEY]) == 0 and file_name not in files_to_delete:
                    files_to_delete.append(file_name)

        for f in files_to_delete:
            self.entries.pop(f)

        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_EXIT}

        return response

    def listen_for_new_client(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_client, args=(client, addr)).start()

    def displayEntries(self):
        print()
        print("CURRENT ENTRIES IN TRACKER...")
        print()
        print(self.entries)

    def listen_to_client(self, client, addr):
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
                        response = self.handle_exit_message(addr)
                    else:
                        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_ERROR_NO_SUCH_MESSAGE_TYPE}
                    self.lock.release()
                client.sendall(json.dumps(response).encode())
            except Exception as e:
                client.close()
                break


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
