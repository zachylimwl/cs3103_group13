TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 65432
P2P_SERVER_HOST = "127.0.0.1"
P2P_SERVER_PORT = 65431
RECEIVE_SIZE_BYTE = 1024
CHUNK_SIZE = 1024
CUSTOM_CHUNK_EXTENSION = ".chunk"
DEFAULT_FILE_DIRECTORY = "test_directory"

MESSAGE_TYPE = "message_type"
FILE_NAME = "file_name"
TRACKER_REQUEST_TYPE_ENTRY = "entry"
TRACKER_REQUEST_TYPE_ADVERTISE = "advertise"
TRACKER_REQUEST_TYPE_QUERY_CHUNKS = "query_chunks"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT = "query_for_content"
TRACKER_REQUEST_TYPE_LIST_ALL = "list_all"
TRACKER_REQUEST_TYPE_EXIT = "exit"

TRACKER_RESPONSE_TYPE_ERROR = "error"
TRACKER_RESPONSE_TYPE_SUCCESS_QUERY_CHUNK_LIST = "success_chunk_list"

PEER_REQUEST_TYPE_CHUNK_DOWNLOAD = "download_chunk"
PEER_REQUEST_TYPE_CHUNK_NUMBER = "download_chunk_number"

TRACKER_REQUEST_TYPE_LIST_ALL_CODE = "1"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT_CODE = "2"
P2P_SERVER_REQUEST_TYPE_DOWNLOAD_CODE = "3"
TRACKER_REQUEST_TYPE_ADVERTISE_CODE = "4"
TRACKER_REQUEST_TYPE_EXIT_CODE = "5"

PAYLOAD_CHECKSUM_KEY = "checksum"
PAYLOAD_FILENAME_KEY = "file_name"
PAYLOAD_PEER_ID_KEY = "peer_id"
PAYLOAD_NUMBER_OF_CHUNKS_KEY = "number_of_chunks"
PAYLOAD_LIST_OF_CHUNKS_KEY = "chunks"
PAYLOAD_LIST_OF_FILES_KEY = "files"

CHUNK_NUMBER_KEY = "chunk_number"
LIST_OF_PEERS_KEY = "list_of_peers"

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