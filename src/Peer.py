from multiprocessing import Process, Queue

from P2pClient import P2pClient
from P2pServer import P2pServer
from constants import *


def listen_for_peers(q):
    server = P2pServer()
    q.put(server.hole_punching())
    server.listen_for_new_peer()


def main():
    client = P2pClient(TRACKER_HOST, TRACKER_PORT)
    client.entry()

    q = Queue()
    # New Thread for peers to download from client
    process = Process(target=listen_for_peers, args=(q,))
    process.start()

    print(OPENING_MESSAGE)

    ext_ip_port = q.get()
    while True:
        option = input("Input: ")

        if option == TRACKER_REQUEST_TYPE_LIST_ALL_AVAILABLE_FILES_CODE:
            client.list_all()
        elif option == TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT_CODE:
            file_name = input("File name: ")
            client.query_for_content(file_name)
        elif option == P2P_SERVER_REQUEST_TYPE_DOWNLOAD_CODE:
            file_name = input("File Name: ")
            client.download_file(file_name)
        elif option == TRACKER_REQUEST_TYPE_ADVERTISE_CODE:
            client.advertise(ext_ip_port)
        elif option == TRACKER_REQUEST_TYPE_EXIT_CODE:
            client.exit()
            client.trackerSocketConnection.close()
            process.terminate()
            break
        else:
            print("You have entered an invalid option.")


main()
