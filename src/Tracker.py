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


    def handle_acquire_message(self, payload):
        peer_id = payload[PAYLOAD_PEER_ID_KEY]

        #process files first

        #if the file is appearing the first time in tracker
        #then add it as a new entry in the dictionary of dictionaries in self.fiel_details
        for file_from_peer in payload[PAYLOAD_LIST_OF_FILES_KEY]:
            file_name = file_from_peer[PAYLOAD_FILENAME_KEY]
            if file_name not in self.file_details:
                file_checksum = file_from_peer[PAYLOAD_CHECKSUM_KEY]
                number_of_chunks = file_from_peer[PAYLOAD_NUMBER_OF_CHUNKS_KEY]
                self.file_details[file_name] = {}
                self.file_details[file_name][PAYLOAD_CHECKSUM_KEY] = file_checksum
                self.file_details[file_name][PAYLOAD_NUMBER_OF_CHUNKS_KEY] = number_of_chunks
            #add owner
            if file_name not in self.file_owners:
                #create new list for that peer_id
                self.file_owners[file_name] = [peer_id]
            #well if the file is there, but this owner is not in the list
            elif peer_id not in self.file_owners[file_name]:
                self.file_owners[file_name].append(peer_id)

        #now we process the chunks
        for chunk_from_peer in payload[PAYLOAD_LIST_OF_CHUNKS_KEY]:
            file_name = chunk_from_peer[PAYLOAD_FILENAME_KEY]
            #if the chunk's file not inside at all
            if file_name not in self.chunk_details:
                self.chunk_details[file_name] = {peer_id: chunk_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]}
            #if the chunk's file is inside, but the peer is not inside
            elif peer_id not in self.chunk_details[file_name]:
                self.chunk_details[file_name][peer_id] = chunk_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]
            else:   #just update the current one
                self.chunk_details[file_name][peer_id] = list(set(self.chunk_details[file_name][peer_id] + chunk_from_peer[PAYLOAD_LIST_OF_CHUNKS_KEY]))  

        return peer_id
    
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
                        peer_id = self.handle_acquire_message(payload)
                        self.lock.release()
                        #if tcp need to ack back ??? then ack using the peer_id (source ip and port all there)
                    elif payload[MESSAGE_TYPE] == TRACKER_REQUEST_TYPE_QUERY_CHUNKS:
                        # Sends list of chunks and owners back to peer
                        chunk_list = create_chunk_list(self, payload[FILE_NAME])
                        client.sendall(json.dumps(file_chunk_response))
                    #create if statements for other types of messages here
                    #if payload[MESSAGE_TYPE] == other request type:
            except Exception as e:
                client.close()
                print(e)


def main():
    tracker = Tracker()
    tracker.listen_for_new_client()


main()
