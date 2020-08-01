# import socket programming library
import socket
import threading
from packet import RequestPacket, ResponsePacket
import requests


class Proxy_Server:
    def __init__(self):
        self.port = 8090
        self.host = ""

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        print("proxy server bound to port", self.port)

        self.s.listen(5)
        print("proxy server is listening")

        while True:
            c, addr = self.s.accept()
            print('Connected to :', addr[0], ':', addr[1])
            t = threading.Thread(target=self.communicate, args=(c,))
            t.start()

    def communicate(self, c: socket.socket):
        while True:
            try:
                data = c.recv(500000)
            except ConnectionResetError:
                break
            print(str(data, 'utf-8'))
            if not data:
                print('Bye')
                break

            req = RequestPacket(str(data, 'utf-8'))
            req.set_main_address()
            # print('--code:', req.code)
            # print('--version', req.request_version)
            # print('--log:', req.log())
            print('--main add:', req.main_address)
            print('--req add:', req.request_address)

            # if req.request_address == '/':
            #     with open("Files/index.html", "rb") as html:
            #         f = html.read()
            #     req.set_file(f, 'text/html')
            #
            # elif req.request_address == '/123.jpg':
            #     with open("Files/123.jpg", "rb") as image:
            #         f = image.read()
            #     if req.can_gzip:
            #         req.set_file(gzip.compress(f), 'image/jpg')
            #     else:
            #         req.set_file(f, 'image/jpg')
            # else:
            #     req.set_file()
            #
            # to_send = ResponsePacket(req).message
            # c.send(to_send)

            # add_to_req = req.main_address
            # if len(req.request_address.split(':')) > 1:
            #     port_to_req = int(req.request_address.split(':')[1])
            # else:
            #     port_to_req = 443
            port_to_req = 80
            # print(req.request_address.split(':'))
            # print((add_to_req, port_to_req))

            try:
                print(req.main_address, req.main_address[0])
                add_to_req = socket.gethostbyname(req.main_address)
                # add_to_req = req.main_address
                print(add_to_req)
                req_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                req_s.connect((add_to_req, port_to_req))
                req_s.send(data)
                new_data = req_s.recv(500000)
                tot_dat = bytes('', 'utf-8')
                # tot_dat+=new_data
                while True:
                    # print('here$$$$$$$$$$$$$$$$$$$')
                    tot_dat += new_data
                    # print(str(new_data, 'utf-8'))
                    try:
                        new_data = req_s.recv(500000)
                    except:
                        new_data = b''
                    if new_data == b'':
                        break
                    # print(str(new_data, 'utf-8'))

                # print(str(tot_dat, 'utf-8'))
                c.send(tot_dat)
                req_s.close()
            except socket.gaierror:

                # this means could not resolve the host
                print('#######################################')
                print("there was an error resolving the host")

        c.close()


proxy = Proxy_Server()
