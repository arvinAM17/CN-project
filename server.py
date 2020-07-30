# import socket programming library
import socket
import threading
from packet import RequestPacket, ResponsePacket
import gzip


class Server:
    def __init__(self):
        self.port = 8080
        self.host = "localhost"

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        print("socket bound to port", self.port)

        self.s.listen(5)
        print("socket is listening")

        while True:
            c, addr = self.s.accept()
            print('Connected to :', addr[0], ':', addr[1])
            t = threading.Thread(target=self.communicate, args=(c,))
            t.start()

    def communicate(self, c: socket.socket):
        while True:
            data = c.recv(1024)
            # print(str(data, 'utf-8'))
            if not data:
                print('Bye')
                break

            req = RequestPacket(str(data, 'utf-8'))
            # print('--code:', req.code)
            # print('--version', req.can_gzip)
            # print('--gzip:', req.can_gzip)

            if req.request_address == '/':
                with open("Files/index.html", "rb") as html:
                    f = html.read()
                req.set_file(f, 'text/html')

            elif req.request_address == '/123.jpg':
                with open("Files" + req.request_address, "rb") as image:
                    f = image.read()

                if req.can_gzip:
                    req.set_file(gzip.compress(f), 'image/jpg')
                else:
                    req.set_file(f, 'image/jpg')
            elif req.request_address == '/text.txt':
                with open("Files" + req.request_address, "rb") as text:
                    f = text.read()

                if req.can_gzip:
                    req.set_file(gzip.compress(f), 'text/plain')
                else:
                    req.set_file(f, 'text/plain')
            else:
                req.set_file()
            print('--log:', req.log())
            to_send = ResponsePacket(req).message
            c.send(to_send)

        c.close()


server = Server()
