# encoding: utf-8
import SocketServer
import logging
from multiprocessing import Process

from service.ab_server_service import AbServerServiceBuilder
from service.ab_service import AbService

HOST = '127.0.0.1'
PORT = 7010
SERVER_URL = (HOST, PORT)
MAX_LENGTH = 1024
MAX_REQUEST = 100


class MyRequestHandler(SocketServer.BaseRequestHandler):

    i = 0
    def __build_service(self, trade_no):
        pass # TODO
    def handle(self):
        buffer = ''
        is_start = True
        msg_size = 0
        idx = 0
        header = None
        while True:
            data = self.request.recv(MAX_LENGTH)

            if data:
                buffer += data
                buf_size = len(buffer)
                if is_start:
                    idx = 41
                    header_text = data[:idx]
                    header = AbService.get_header_from_text(header_text)
                    msg_size = header.msg_size
                if msg_size >= buf_size - idx:
                    break

                # self.do_event(data)
                # self.request.sendall(data)
                is_start = False
            else:
                break
        if buffer and header:
            ss = AbServerServiceBuilder.create_service(header.trade_no)
            r = ss.do_event(data=buffer)
        self.request.close()

    # def do_event(self, data):
    #     self.__class__.i += 1
    #     self.buffer (data)
        # print(str(self.__class__.i) + ': ' + str(data))


def _start_server():
    server = SocketServer.ThreadingTCPServer(SERVER_URL, MyRequestHandler)
    server.request_queue_size = MAX_REQUEST
    server.serve_forever()


def start_ab_server():
    # freeze_support()
    try:
        p = Process(target=_start_server)
        p.start()
    except Exception as e:
        logging.exception(e)
        raise e
