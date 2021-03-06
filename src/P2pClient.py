import socket
import json
import os
import hashlib
from pynat import *
from random import randint
from constants import *
from FileUtilities import *


class P2pClient:
    def __init__(self, tracker_host, tracker_port):
        self.trackerSocketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.trackerSocketConnection.connect((tracker_host, tracker_port))
        host_port_tuple = self.trackerSocketConnection.getsockname()
        self.host = host_port_tuple[0]
        self.port = host_port_tuple[1]
        self.files = []
        self.chunks = []
        self.ext_ip_port = None
        
        if (os.path.isdir(DEFAULT_FILE_DIRECTORY)):
            os.chdir(DEFAULT_FILE_DIRECTORY)
        else:
            print("\n\nDefault file directory not found in client, and will be created...\n\n")
            os.mkdir(DEFAULT_FILE_DIRECTORY)
            os.chdir(DEFAULT_FILE_DIRECTORY)
        self.directory = os.getcwd()
        pass

    # Download chunk from peer
    def download_chunk_from_peer(self, file_name, chunk_number, chunk_details, ext_ip_port):
        peer_list = chunk_details[LIST_OF_PEERS_KEY]
        # Uses a random peer for now
        random_peer_index = randint(0, len(peer_list) - 1)
        peer = peer_list[random_peer_index]

        internal_ip = peer[0]
        external_ip = peer[1]

        internal_peer_ip = internal_ip.split(":")[0]
        internal_peer_port = int(internal_ip.split(":")[1])
        external_peer_ip = external_ip.split(":")[0]
        external_peer_port = int(external_ip.split(":")[1])
        
        file_chunk_request = self.create_file_chunk_request(file_name, chunk_number)
        # Retrieve chunk data from peer
        response = self.send_to_peer(file_chunk_request, internal_peer_ip, internal_peer_port)
        if response is None:
            print("Internal IP connection failed")
            response = self.send_to_peer(file_chunk_request, external_peer_ip, internal_peer_port)
            if response is None:
                print("External IP connection failed")
                print("Peer cannot be found")
                return
        # Do Checksum check
        file_checksum = chunk_details[PAYLOAD_CHECKSUM_KEY]
        response_checksum = hashlib.md5(response).hexdigest()
        if (file_checksum == response_checksum):
            print("Downloading Chunk " + str(chunk_number) + " from peer")
            save_file_chunk(response, file_name, chunk_number, self.directory)
            request = self.create_advertise_chunk_request(file_name, chunk_number, file_checksum, ext_ip_port)
            print("Informing Tracker about chunk" + str(chunk_number) + " of " + file_name)
            self.send_to_tracker(request)
        else:
            print("Error in downloading chunk " + str(chunk_number) + "of file: " + file_name + ". Please download the file again")

    # Create an advertise message request with the same format as the advertiser
    # {
    # 'peer_id': '127.0.0.1:65434', 
    # 'files': [], 
    # 'chunks': [{'file_name': 'file2.txt', 'chunks': [('1', '5fc51937c2e9e7f2e5971e2ec8e4f88b')]}], 
    # 'message_type': 'advertise'
    # }
    def create_advertise_chunk_request(self, file_name, chunk_number, checksum, ext_ip_port):
        request = {}
        if (ext_ip_port == OPEN or ext_ip_port == BLOCKED):
            request[PAYLOAD_PUBLIC_PEER_ID_KEY] = None
        else:
            request[PAYLOAD_PUBLIC_PEER_ID_KEY] = ext_ip_port
        
        request[PAYLOAD_PEER_ID_KEY] = str(str(self.host) + ":" + str(P2P_SERVER_PORT))
        files = []
        request[PAYLOAD_LIST_OF_FILES_KEY] = files
        chunk_keys = [{PAYLOAD_LIST_OF_CHUNKS_KEY: [(int(chunk_number), checksum)], PAYLOAD_FILENAME_KEY: file_name}]
        request[PAYLOAD_LIST_OF_CHUNKS_KEY] = chunk_keys
        request[MESSAGE_TYPE] = TRACKER_REQUEST_TYPE_ADVERTISE
        return request

    # Used for sending request to peer and retrieving the file chunk
    def send_to_peer(self, request, peer_ip, peer_port):
        print("Connecting to Peer (" + str(peer_ip) + ":" + str(peer_port) + ")")
        sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sending_socket.settimeout(5)
        try:
            sending_socket.connect((peer_ip, peer_port))
            sending_socket.sendall(json.dumps(request).encode())
            # Receive data
            recv = sending_socket.recv(1024)
            sending_socket.close()
            return recv
        except:
            return None

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

    def advertise(self, external_ip_port):
        self.process_directory()
        request = self.craft_payload_for_tracker(external_ip_port)
        self.send_to_tracker(request)
        print("Details of files sent to Tracker.")

    def query_for_content(self, file_name):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT,
                   PAYLOAD_FILENAME_KEY: file_name,
                   }
        response = self.send_to_tracker(request)

        if response[MESSAGE_TYPE] == TRACKER_FILE_NOT_FOUND:
            print("File is not found on server.")
        elif response[MESSAGE_TYPE] == TRACKER_PEERS_NOT_FOUND:
            print("No peers are available for this file")
        else:
            print("File is ready for download")

    def download_file(self, file_name, ext_ip_port):
        # Queries for list of chunks and owner from tracker
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_QUERY_CHUNKS, FILE_NAME: file_name}
        print("Requesting list of chunks from Tracker...")
        response = self.send_to_tracker(request)

        # Handle file not found
        if response[MESSAGE_TYPE] == TRACKER_RESPONSE_TYPE_ERROR:
            print("Requested File does not exist.")
            return

        # Send to P2P server to request for download
        chunk_keys = list(response[CHUNK_LIST].keys())
        for chunk_key in chunk_keys:
            if does_file_exist(create_chunk_file_name(file_name, chunk_key), self.directory):
                print("Chunk " + str(chunk_key) + "already exists. Skipping download")
            else:
                self.download_chunk_from_peer(file_name, chunk_key, response[CHUNK_LIST][chunk_key], ext_ip_port)
        
        # Check if all chunks are downloaded
        for chunk_key in chunk_keys:
            if not does_file_exist(create_chunk_file_name(file_name, chunk_key), self.directory):
                print("Chunk " + str(chunk_key) + " cannot be found. Please download the file again.")
                return
        print("Combining all chunks")
        combine_chunks(file_name, len(chunk_keys), self.directory)
        
    def list_all(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES}

        response = self.send_to_tracker(request)
        available_files = response[LIST_OF_FILES]

        print(LIST_ALL_MESSAGE)
        for f in available_files:
            print(f)
        print(END_MESSAGE)

    def exit(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_EXIT,
                   PAYLOAD_PUBLIC_PEER_ID_KEY: self.ext_ip_port,
                   PAYLOAD_PEER_ID_KEY: str(str(self.host) + ":" + str(self.port))}

        response = self.send_to_tracker(request)

        if response[MESSAGE_TYPE] == TRACKER_RESPONSE_TYPE_EXIT:
            print(EXIT_MESSAGE)
            print(END_MESSAGE)

    #Create the message payload for advertise to be sent to the Tracker
    # payload = {
    #     "peer_id": source_ip i.e. 127.0.0.1 for example
    #     "files": [{"checksum": "checksum", "num_of_chunks": 1, "filename": "test_c"}, ...],
    #     "chunks": [{"chunks": [1, 2, 3, 4, 5], "filename": "test_b"}, ...]
    #     "message_type": "INFORM_AND_UPDATE",
    # }
    def craft_payload_for_tracker(self, external_ip_port):
        payload = {}
        if (external_ip_port == OPEN or external_ip_port == BLOCKED):
            payload[PAYLOAD_PUBLIC_PEER_ID_KEY] = None
        else:
            payload[PAYLOAD_PUBLIC_PEER_ID_KEY] = external_ip_port
        
        payload[PAYLOAD_PEER_ID_KEY] = str(str(self.host) + ":" + str(P2P_SERVER_PORT))
        payload[PAYLOAD_LIST_OF_FILES_KEY] = self.files
        payload[PAYLOAD_LIST_OF_CHUNKS_KEY] = self.chunks
        payload[MESSAGE_TYPE] = TRACKER_REQUEST_TYPE_ADVERTISE
        return payload

    def send_to_tracker(self, request):
        try:
            self.trackerSocketConnection.sendall(json.dumps(request).encode())
            response = json.loads(self.trackerSocketConnection.recv(RECEIVE_SIZE_BYTE))
            return response
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
            chunk_number = int(arr[1])
            if file_name in dic:
                dic[file_name].append((chunk_number, checksum))
            else:
                dic[file_name] = [(chunk_number, checksum)]

        for file_name, list_of_chunks in dic.items():
            res.append({PAYLOAD_FILENAME_KEY: file_name, PAYLOAD_LIST_OF_CHUNKS_KEY: list_of_chunks})
        return res

    def chunks_from_whole_file(self):
        for f in self.files:
            dic = {}
            #split files into chunks, make checksum, add to self.chunks
            number_of_chunks = f[PAYLOAD_NUMBER_OF_CHUNKS_KEY]
            chunk_numbers = range(number_of_chunks)
            file_name = f[PAYLOAD_FILENAME_KEY]
            dic[PAYLOAD_FILENAME_KEY] = file_name
            dic[PAYLOAD_LIST_OF_CHUNKS_KEY] = []
            full_path = os.path.join(self.directory, file_name)
            with open(full_path, "rb") as chunk_file:
                for i in chunk_numbers:
                    #seek the chunk 
                    chunk_file.seek(i * CHUNK_SIZE)
                    chunk_file_bytes = chunk_file.read(CHUNK_SIZE)
                    #checksum
                    checksum = hashlib.md5(chunk_file_bytes).hexdigest()
                    #put this in the dic
                    dic[PAYLOAD_LIST_OF_CHUNKS_KEY].append((i+1, checksum))

            
            self.chunks.append(dic)
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
        self.chunks_from_whole_file()
