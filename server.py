# import socket programming library
import socket
import threading
from packet import RequestPacket, ResponsePacket
import gzip


class Server:
    def __init__(self):
        self.port = 12345
        self.host = ""

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
            print(str(data, 'utf-8'))
            if not data:
                print('Bye')
                break

            req = RequestPacket(str(data, 'utf-8'))
            print('--code:', req.code)
            print('--version', req.can_gzip)
            print('--log:', req.log())

            if req.request_address == '/':
                with open("Files/index.html", "rb") as html:
                    f = html.read()
                req.set_file(f, 'text/html')

            elif req.request_address == '/123.jpg':
                with open("Files/123.jpg", "rb") as image:
                    f = image.read()
                if req.can_gzip:
                    req.set_file(gzip.compress(f), 'image/jpg')
                else:
                    req.set_file(f, 'image/jpg')
            else:
                req.set_file()
            to_send = ResponsePacket(req).message
            c.send(to_send)

        c.close()


server = Server()
