TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 65432
P2P_SERVER_HOST = "127.0.0.1"
P2P_SERVER_PORT = 65433
RECEIVE_SIZE_BYTE = 1024


MESSAGE_TYPE = "message_type"
TRACKER_REQUEST_TYPE_ENTRY = "entry"
TRACKER_REQUEST_TYPE_ADVERTISE = "advertise"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT = "query_for_content"
TRACKER_REQUEST_TYPE_LIST_ALL = "list_all"
TRACKER_REQUEST_TYPE_EXIT = "exit"

TRACKER_REQUEST_TYPE_LIST_ALL_CODE = "1"
TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT_CODE = "2"
TRACKER_REQUEST_TYPE_ADVERTISE_CODE = "4"
TRACKER_REQUEST_TYPE_EXIT_CODE = "5"

P2P_SERVER_REQUEST_TYPE_DOWNLOAD_CODE = "3"


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
