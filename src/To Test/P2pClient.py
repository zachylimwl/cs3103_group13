import socket
import json
import os
import hashlib
from random import randint
from constants import *
from FileUtilities import *

class P2pClient:
    def __init__(self, host, port):
        self.trackerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.trackerSocket.connect((host, port))
        self.host = host    #need determine the ID of the peer. Use host?
        self.port = port
        self.files = []
        self.chunks = []
        #currently set to default file path... 
        #should include arg parser with flags e.g. "python Peer.py --dir my_directory_path"
        os.chdir(DEFAULT_FILE_DIRECTORY)
        self.directory = os.getcwd()
        pass

    # Download chunk from peer
    def download_chunk_from_peer(self, file_name, chunk_number, chunk_details):
        print(chunk_details)
        # Check if chunk exist ### IMPLEMENT
        peer_list = chunk_details[LIST_OF_PEERS_KEY]
        # Uses a random peer for now
        random_peer_index = randint(0, len(peer_list) - 1)
        peer = peer_list[random_peer_index]
        peer_ip = P2P_SERVER_HOST ### IMPLEMENT get from ben
        peer_port = 65433 ### IMPLEMENT get from ben
        file_chunk_request = self.create_file_chunk_request(file_name, chunk_number)
        # Retrieve chunk data from peer
        response = self.send_to_peer(file_chunk_request, peer_ip, peer_port)
        print("FILE DATA RECEIVED:")
        print(response)
        save_file_chunk(response, file_name, chunk_number, self.directory)

    # Used for sending request to peer and retrieving the file chunk
    def send_to_peer(self, request, peer_ip, peer_port):
        sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sending_socket.connect((peer_ip, peer_port))
        sending_socket.sendall(json.dumps(request).encode())
        # Receive data
        recv = sending_socket.recv(1024)
        sending_socket.close()
        return recv

    # Creates the message request for requesting a file chunk from another peer
    # Format:
    # {
    #   MESSAGE_TYPE : PEER_REQUEST_TYPE_CHUNK_DOWNLOAD
    #   FILE_NAME : file_name
    #   PEER_REQUEST_CHUNK_NUMBER = chunk_number
    # }
    def create_file_chunk_request(self, file_name, chunk_number):
        request = {}
        request[MESSAGE_TYPE] = PEER_REQUEST_TYPE_CHUNK_DOWNLOAD
        request[FILE_NAME] = file_name
        request[PEER_REQUEST_TYPE_CHUNK_NUMBER] = chunk_number
        return request

    def entry(self):
        request = {}
        request[MESSAGE_TYPE] = TRACKER_REQUEST_TYPE_ENTRY
        self.send_to_tracker(request)

    def advertise(self):
        self.process_directory()
        request = self.craft_payload_for_tracker()
        self.send_to_tracker(request)

    def query_for_content(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT}
        self.send_to_tracker(request)

    def download_file(self, file_name):
        # Queries for list of chunks and owner from tracker
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_QUERY_CHUNKS, FILE_NAME: file_name}
        print(request)
        self.send_to_tracker(request)
        response = self.receive_from_tracker()
        print(response)
        # Handle any potential file not found
        if response[MESSAGE_TYPE] == TRACKER_RESPONSE_TYPE_ERROR:
            print("File does not exist.")
            return
        chunk_keys = list(response[file_name].keys())
        print(chunk_keys)
        # Send to P2P server to request for download
        for chunk_key in chunk_keys:
            self.download_chunk_from_peer(file_name, chunk_key, response[file_name][chunk_key])
            ### IMPLEMENT send file for advertising
        ### Check if chunk is completed
        combine_chunks(file_name, len(chunk_keys), self.directory)
        
    def list_all(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_LIST_ALL}
        self.send_to_tracker(request)

    def exit(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_EXIT}
        self.send_to_tracker(request)
    

    #Create the message payload for advertise to be sent to the Tracker
    # payload = {
    #     "peer_id": source_ip + : + source_port i.e. 127.0.0.1:1880 for example
    #     "files": [{"checksum": "checksum", "num_of_chunks": 1, "filename": "test_c"}, ...],
    #     "chunks": [{"chunks": [1, 2, 3, 4, 5], "filename": "test_b"}, ...]
    #     "message_type": "INFORM_AND_UPDATE",
    # }
    def craft_payload_for_tracker(self):
        payload = {}
        payload[PAYLOAD_PEER_ID_KEY] = str(self.host) + ":" + str(self.port)
        payload[PAYLOAD_LIST_OF_FILES_KEY] = self.files
        payload[PAYLOAD_LIST_OF_CHUNKS_KEY] = self.chunks
        payload[MESSAGE_TYPE] = TRACKER_REQUEST_TYPE_ADVERTISE
        return payload


    def send_to_tracker(self, request):
        try:
            self.trackerSocket.sendall(json.dumps(request).encode())
        except Exception as e:
            print(e)

    # Receives a response from the tracker
    def receive_from_tracker(self):
        try:
            data = self.trackerSocket.recv(RECEIVE_SIZE_BYTE)
            received_data = json.loads(data)
            return received_data
        except Exception as e:
            print(e)
        

    #Change file to a dictionary format
    # res = {"checksum": checksum_string,
    #       "number_of_chunks": 37
    #       "file_name": file_name_string}
    def format_whole_file(self, file_name):
        res = {}
        full_path = os.path.join(self.directory, file_name)
        checksum = hashlib.md5(open(full_path, 'rb').read()).hexdigest()
        file_size = os.stat(full_path).st_size
        leftover_bytes = file_size % CHUNK_SIZE
        if leftover_bytes == 0:
            number_of_chunks = int(file_size / CHUNK_SIZE)
        else:
            number_of_chunks = int((file_size / CHUNK_SIZE) + 1)

        res[PAYLOAD_CHECKSUM_KEY] = checksum
        res[PAYLOAD_NUMBER_OF_CHUNKS_KEY] = number_of_chunks
        res[PAYLOAD_FILENAME_KEY] = file_name
        return res

    #Change chunk to a dictionary format as well
    #res = {"chunks": [1,2,3,4],
    #       "file_name": file_name_string,
    #      }
    #return the list of res, i.e. [{"chunks": [(1, checksum), (2, checksum)...], "file_name": f1},
    #  {"chunks": [(1, checksum), (2, checksum)...], "file_name": f2}... ]
    def format_chunk(self, chunks):
        #naming convention: "file_name"_"chunk_number".chunk
        #e.g. script_3.chunk
        dic = {}
        res = [] 
        for ch in chunks:
            chunk_path = os.path.join(self.directory, ch)
            checksum = hashlib.md5(open(chunk_path, 'rb').read()).hexdigest()
            string = ch.rsplit(".", 1)
            arr = string[0].rsplit("_", 1)
            file_name = arr[0]
            chunk_number = arr[1]
            if file_name in dic:
                dic[file_name].append((chunk_number, checksum))
            else:
                dic[file_name] = [(chunk_number, checksum)]

        for file_name, list_of_chunks in dic.items():
            res.append({PAYLOAD_FILENAME_KEY: file_name, PAYLOAD_LIST_OF_CHUNKS_KEY: list_of_chunks})
        return res

    #Process the directory
    #sets information in self.files, and self.chunks
    def process_directory(self):
        #get files from the directory
        files_in_dir = []
        for f in os.walk(self.directory):
            for filename in f[2]:
                full_file_path = os.path.join(self.directory, filename)
                if os.path.isfile(full_file_path):
                    files_in_dir.append(filename)
        
        #if the files are not in the form of xxx.chunk, then it's a whole file
        files = [i for i in files_in_dir if i[-6:] != CUSTOM_CHUNK_EXTENSION]
        #else, it's a chunk
        chunks = [i for i in files_in_dir if i[-6:] == CUSTOM_CHUNK_EXTENSION]
        #format the files and chunks to our standard, then put in self
        self.files = [self.format_whole_file(j) for j in files]
        self.chunks = self.format_chunk(chunks)
    