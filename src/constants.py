TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 65432
P2P_SERVER_HOST = "127.0.0.1"
P2P_SERVER_PORT = 65433
RECEIVE_SIZE_BYTE = 1024
CHUNK_SIZE = 1024
CUSTOM_CHUNK_EXTENSION = ".chunk"
DEFAULT_FILE_DIRECTORY = "../test_directory"

#Message type
MESSAGE_TYPE = "message_type"
TRACKER_REQUEST_TYPE_ENTRY = "entry"
TRACKER_REQUEST_TYPE_ADVERTISE = "advertise"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT = "query_for_content"
TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES = "list_all"
TRACKER_REQUEST_TYPE_EXIT = "exit"

#Tracker request
TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES_CODE = "1"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT_CODE = "2"
P2P_SERVER_REQUEST_TYPE_DOWNLOAD_CODE = "3"
TRACKER_REQUEST_TYPE_ADVERTISE_CODE = "4"
TRACKER_REQUEST_TYPE_EXIT_CODE = "5"

TRACKER_RESPONSE_TYPE_LIST_ALL_AVAILABLE_FILES = 'all_available_files_received'
LIST_OF_FILES = 'list_of_files'

#Payload
PAYLOAD_CHECKSUM_KEY = "checksum"
PAYLOAD_FILENAME_KEY = "file_name"
PAYLOAD_PEER_ID_KEY = "peer_id"
PAYLOAD_NUMBER_OF_CHUNKS_KEY = "number_of_chunks"
PAYLOAD_LIST_OF_CHUNKS_KEY = "chunks"
PAYLOAD_LIST_OF_FILES_KEY = "files"
PAYLOAD_FILE_CHUNK_ID_KEY = "chunk_id"

CHUNK_NUMBER_KEY = "chunk_number"
LIST_OF_PEERS_KEY = "list_of_peers"

#Success message type
TRACKER_DOWNLOAD_AVAILABLE = "download_available"
TRACKER_PEERS_AVAILABLE = "peers_available"

#Error message type
TRACKER_FILE_NOT_FOUND = "file_not_found"
TRACKER_PEERS_NOT_FOUND = "peers_not_found"
TRACKER_CHUNK_NOT_FOUND = "chunk_not_found"


OPENING_MESSAGE = """
========================================================================

CS3103 P2P Client. Please choose from the following list of commands:

========================================================================

1. List all files
Enter: 1

2. List peers with the file you want
Enter: 2

3. Download file
Enter: 3

4. Update tracker of your files
Enter: 4

5. Exit the p2p client
Enter: 5
"""

LIST_ALL_MESSAGE = """
-------------------------------------------
These are the available files for download:
"""

END_MESSAGE = "-------------------------------------------"

