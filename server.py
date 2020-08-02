# import socket programming library
import socket
import threading
from packet import RequestPacket, ResponsePacket
import gzip, time, constants


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

    @staticmethod
    def communicate(c: socket.socket):
        time_to_stop = time.time() + 1200
        while True:
            if time_to_stop <= time.time():
                break
            data = c.recv(1024)
            # print(str(data, 'utf-8'))
            if not data or time_to_stop <= time.time():
                print('Bye')
                break

            req = RequestPacket(str(data, 'utf-8'))
            print('--code:', req.code)
            print('--version', req.request_version)
            print('--log:', req.log())
            print('--add:', req.main_address)

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

            if req.connection_type == constants.CLOSED:
                break
            else:
                time_to_stop = time.time() + req.timer

        c.close()


server = Server()
