# import socket programming library
import socket
import threading
from packet import RequestPacket, ResponsePacket


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
            print(req.connection_type)

            # data = data[::-1]
            # c.send(data)

        c.close()


server = Server()
