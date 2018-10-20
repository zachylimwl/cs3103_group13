import socket
import json
from constants import *


class P2pClient:
    def __init__(self, host, port):
        self.trackerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.trackerSocket.connect((host, port))
        pass

    def entry(self):
        request = { MESSAGE_TYPE: TRACKER_REQUEST_TYPE_ENTRY}
        self.send_to_tracker(request)

    def advertise(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_ADVERTISE}
        self.send_to_tracker(request)

    def query_for_content(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_QUERY_FOR_CONTENT}
        self.send_to_tracker(request)

    def list_all(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_LIST_ALL}
        self.send_to_tracker(request)

    def exit(self):
        request = {MESSAGE_TYPE: TRACKER_REQUEST_TYPE_EXIT}
        self.send_to_tracker(request)

    def send_to_tracker(self, request):
        try:
            self.trackerSocket.sendall(json.dumps(request).encode())
        except Exception as e:
            print(e)

