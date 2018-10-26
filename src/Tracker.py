import socket
import threading
from threading import Lock
import json
import queue

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

        self.ip_port_to_id = {}
        self.id_to_ip_port = {}
        self.ip_port_index = 0
        self.freed_ip_port_indexes = queue.Queue(maxsize=0)

    def handle_advertise_message(self, payload):
        peer_id = payload[PAYLOAD_PEER_ID_KEY]
        if peer_id not in self.ip_port_to_id:
            if self.freed_ip_port_indexes.empty():
                self.ip_port_to_id[peer_id] = self.ip_port_index
                self.id_to_ip_port[self.ip_port_index] = peer_id
                self.ip_port_index += 1
            else:
                index = self.freed_ip_port_indexes.get()
                self.ip_port_to_id[peer_id] = index
                self.id_to_ip_port[index] = peer_id

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
            fileName = chunks_of_file_from_peer[PAYLOAD_FILENAME_KEY]
            #for every chunk of the file
            for ch in chunks_of_file_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]:
                chunk_num = ch[0]
                checksum = ch[1]

                #if chunk number not in the entries  
                if chunk_num not in self.entries[file_name]:
                    self.entries[file_name][chunk_num] = {}
                    self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY] = []
                    self.entries[file_name][chunk_num][PAYLOAD_CHECKSUM_KEY] = checksum
                    self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                #if the chunk's file is inside, but the peer is not inside
                elif peer_id not in self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY]:
                    self.entries[file_name][chunk_num][LIST_OF_PEERS_KEY].append(peer_id)
                #else:

        return peer_id

    def obtain_single_packet_query(self, payload):
        request = {}
        file_name = payload[PAYLOAD_FILENAME_KEY]
        list_of_peer_chunks = payload[PAYLOAD_LIST_OF_CHUNKS_KEY]
        if file_name not in self.entries:
            request[MESSAGE_TYPE] = TRACKER_FILE_NOT_FOUND
            return request

        # If user has all chunks
        if len(self.entries[file_name]) == len(list_of_peer_chunks):
            request[MESSAGE_TYPE] = TRACKER_ALL_CHUNKS_DOWNLOADED
            return request

        list_of_chunks_needed = []
        for chunk in self.entries[file_name]:
            if chunk not in list_of_peer_chunks:
                list_of_chunks_needed.append(chunk)
        
        # No chunks of file could be found
        if list_of_chunks_needed.empty():
            request[MESSAGE_TYPE] = TRACKER_CHUNKS_NOT_FOUND
            return request

        # Uses the first chunk. Need change to priority based (Priority Queue)
        chunk_id = list_of_chunks_needed[0]
        if chunk_id.empty():
            request[MESSAGE_TYPE] = TRACKER_PEERS_NOT_FOUND
            return request
        
        request[MESSAGE_TYPE] = TRACKER_DOWNLOAD_AVAILABLE
        request[PAYLOAD_PEER_ID_KEY] = id_to_ip_port.get(self.entries[file_name][chunk_id][0]) # Get first user in list. Need change
        request[CHUNK_NUMBER_KEY] = chunk_id
        request[PAYLOAD_FILENAME_KEY] = file_name
        return request
    
    def handle_content_query(self, payload):
        request = {}
        file_name = payload[PAYLOAD_FILENAME_KEY]
        if file_name not in self.entries:
            request[MESSAGE_TYPE] = TRACKER_FILE_NOT_FOUND
            return request

        request[MESSAGE_TYPE] = TRACKER_PEERS_AVAILABLE
        chunk_peer_list = {}
        for chunk in self.entries[file_name]:
            chunk_peer_list.append(chunk)
            for peer in chunk_peer_list[chunk]:
                chunk_peer_list[chunk][peer] = id_to_ip_port(chunk_peer_list[chunk][peer]) # Convert id to ip:port

        request[LIST_OF_PEERS_KEY] = chunk_peer_list
        return request

    def handle_list_all_available_files_message(self):
        all_available_files = list(self.entries.keys()) if len(self.entries.keys()) else []

        response = {MESSAGE_TYPE: TRACKER_RESPONSE_TYPE_LIST_ALL_AVAILABLE_FILES,
                    LIST_OF_FILES: all_available_files}

        return response

    def listen_for_new_client(self):
        self.socket.listen()
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen_to_client, args=(client,)).start()

    def listen_to_client(self, client):
        response = {}
        while True:
            try:
                data = client.recv(RECEIVE_SIZE_BYTE)
                if data:
                    payload = json.loads(data)
                    self.lock.acquire()
                    if payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_ADVERTISE:
                        peer_id = self.handle_advertise_message(payload)
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT:
                        response = self.handle_content_query(payload)
                        #if tcp need to ack back ??? then ack using the peer_id (source ip and port all there)
                    #create if statements for other types of messages here
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES:
                        response = self.handle_list_all_available_files_message()
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_EXIT:
                        pass
                    else:
                        pass
                    self.lock.release()
                client.sendall(json.dumps(response).encode())
            except Exception as e:
                client.close()
                print(e)


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
