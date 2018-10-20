import threading

from P2pClient import P2pClient
from P2pServer import P2pServer
from constants import *


def listen_for_peers():
    server = P2pServer()
    server.listen_for_new_peer()


def main():
    client = P2pClient(TRACKER_HOST, TRACKER_PORT)
    client.entry()

    # New Thread for peers to download from client
    threading.Thread(target=listen_for_peers).start()

    print(OPENING_MESSAGE)

    while True:
        option = input("Input: ")

        if option == TRACKER_REQUEST_TYPE_LIST_ALL_CODE:
            client.list_all()
        elif option == TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT_CODE:
            client.query_for_content()
        elif option == P2P_SERVER_REQUEST_TYPE_DOWNLOAD_CODE:
            pass
        elif option == TRACKER_REQUEST_TYPE_ADVERTISE_CODE:
            client.advertise()
        elif option == TRACKER_REQUEST_TYPE_EXIT_CODE:
            client.exit()
        else:
            print("You have entered an invalid option.")


main()
