# import socket programming library
import socket
import threading
from packet import RequestPacket


class ProxyServer:
    packet_server_length = []
    packet_client_length = []
    body_server_length = []

    def __init__(self):
        self.telnet_port = 8091
        self.telnet_host = '127.0.0.1'
        self.proxy_port = 8090
        self.proxy_host = '127.0.0.1'
        self.s_telnet = None
        self.s_proxy = None
        proxy_thread = threading.Thread(target=self.proxy, args=())
        telnet_thread = threading.Thread(target=self.telnet, args=())
        proxy_thread.start()
        telnet_thread.start()
        # TODO

    def proxy(self):
        self.s_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_proxy.bind((self.proxy_host, self.proxy_port))
        print("proxy server bound to port", self.proxy_port)

        self.s_proxy.listen(5)
        print("proxy server is listening")

        while True:
            c, address = self.s_proxy.accept()
            print('Connected to :', address[0], ':', address[1])
            t = threading.Thread(target=self.proxy_communicate, args=(c,))
            t.start()

    @staticmethod
    def proxy_communicate(c: socket.socket):
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
            print('--main add:', req.main_address)
            print('--req add:', req.request_address)

            port_to_req = 80

            try:
                print(req.main_address, req.main_address[0])
                add_to_req = socket.gethostbyname(req.main_address)
                print(add_to_req)
                req_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                req_s.connect((add_to_req, port_to_req))
                req_s.send(data)
                new_data = req_s.recv(500000)
                tot_dat = bytes('', 'utf-8')
                while True:
                    tot_dat += new_data
                    try:
                        new_data = req_s.recv(500000)
                    except:
                        new_data = b''
                    if new_data == b'':
                        break

                c.send(tot_dat)
                req_s.close()
            except socket.gaierror:
                print('#######################################')
                print("there was an error resolving the host")

        c.close()

    def telnet(self):
        self.s_telnet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_telnet.bind((self.telnet_host, self.telnet_port))
        print("proxy server bound to port", self.telnet_port)

        self.s_telnet.listen(5)
        print("proxy server is listening")

        while True:
            c, address = self.s_telnet.accept()
            print('Connected to :', address[0], ':', address[1])
            t = threading.Thread(target=self.telnet_communicate, args=(c,))
            t.start()

    def telnet_communicate(self, c: socket.socket):
        command = ''
        while True:
            try:
                data = c.recv(500000)
            except ConnectionResetError:
                break

            char = str(data, 'utf-8')
            if not data:
                print('Bye')
                break
            if char != ';':
                command += char
            else:
                print(command)
                c.send(bytes('\r' + command + '\n\r' + self.get_command_response(command), 'utf-8'))
                command = ''

        c.close()

    @staticmethod
    def get_command_response(command: str) -> str:
        response = ''
        # if command
        # TODO
        response += '\n\r'
        return response


proxy = ProxyServer()
# telnet = TelnetListener()
