# import socket programming library
import socket, constants
import threading
from packet import RequestPacket, ResponsePacket
import numpy as np
import constants


class ProxyServer:
    connection_data = {'pls': {'ps': [], 'pc': [], 'bs': []},
                       'type': {'t/h': 0, 't/p': 0, 'i/p': 0, 'i/jpg': 0, 'i/jpeg': 0},
                       'stat': {200: 0, 301: 0, 304: 0, 400: 0, 404: 0, 405: 0, 501: 0},
                       'visited': {}}

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
            print('\nConnected to :', address[0], ':', address[1])
            t = threading.Thread(target=self.proxy_communicate, args=(c, address,))
            t.start()

    def proxy_communicate(self, c: socket.socket, client_address):
        while True:
            try:
                data = c.recv(500000)
            except ConnectionResetError or OSError:
                break
            # print(str(data, 'utf-8'))
            if not data:
                print('Bye')
                break

            self.update_connection_data(data, False, 0)

            req = RequestPacket(str(data, 'utf-8'))
            req.set_main_address()
            # print('--main add:', req.main_address)
            # print('--req add:', req.request_address)
            print('\nREQUEST: ',
                  '[' + ResponsePacket.get_date() + '] [' + str(client_address[0]) + ' : ' + str(client_address[
                                                                                                     1]) + '] [' + req.main_address + ' : 80] "' + req.request_string() + '"')
            to_close = req.connection_type

            connected_servers = dict()

            port_to_req = 80

            try:
                # print(req.main_address, req.main_address[0])
                add_to_req = socket.gethostbyname(req.main_address)
                # print(add_to_req)

                if add_to_req not in connected_servers.keys():
                    connected_servers[add_to_req] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    connected_servers[add_to_req].connect((add_to_req, port_to_req))
                connected_servers[add_to_req].send(data)
                new_data = connected_servers[add_to_req].recv(500000)
                tot_dat = bytes('', 'utf-8')
                while True:
                    tot_dat += new_data
                    try:
                        new_data = connected_servers[add_to_req].recv(500000)
                    except OSError:
                        new_data = b''
                    if new_data == b'':
                        break

                cut_off = 0
                try:
                    _temp = str(tot_dat, 'utf-8')
                    print('\nRESPONSE:',
                          '[' + ResponsePacket.get_date() + '] [' + str(client_address[0]) + ' : ' + str(client_address[
                                                                                                             1]) + '] [' + req.main_address + ' : 80] "' +
                          str(tot_dat, 'utf-8').split('\n\r')[
                              0].split('\r')[0] + '" for "' + req.request_string() + '"')

                except UnicodeDecodeError as e:
                    # print('%%%%%%%%%%%%%%%%%%')
                    # print('%%%%%%%%%%%%%%%%%%')
                    # print(e.__str__().split(':')[0].split(' ')[-1])
                    cut_off = int(e.__str__().split(':')[0].split(' ')[-1])
                    print('\nRESPONSE:',
                          '[' + ResponsePacket.get_date() + '] [' + str(client_address[0]) + ' : ' + str(client_address[
                                                                                                             1]) + '] [' + req.main_address + ' : 80] "' +
                          str(tot_dat[:cut_off], 'utf-8').split('\n\r')[
                              0].split('\r')[0] + '" for "' + req.request_string() + '"')
                    # print('%%%%%%%%%%%%%%%%%%')
                    # print('%%%%%%%%%%%%%%%%%%')

                # print('---------arvin---------')
                # print('---------tot data' + str((tot_dat[:cut_off] if cut_off > 0 else tot_dat), 'utf-8'))
                # print('RESPONSE: ',
                #       '[' + ResponsePacket.get_date() + '] [' + str(client_address[0]) + ' : ' + str(client_address[
                #           1]) + '] [' + req.main_address + ' : 80] "' +
                #       str((tot_dat[:cut_off] if cut_off > 0 else tot_dat), 'utf-8').split('\n')[
                #           0] + '" for "' + req.request_string() + '"')

                self.update_connection_data(tot_dat, True, cut_off)
                c.send(tot_dat)
                if cut_off == 0:
                    if to_close == constants.CLOSED or RequestPacket(
                            str(tot_dat, 'utf-8')).connection_type == constants.CLOSED:
                        connected_servers[add_to_req].close()
                        del connected_servers[add_to_req]
                        break
                else:
                    if to_close == constants.CLOSED or RequestPacket(
                            str(tot_dat[:cut_off], 'utf-8')).connection_type == constants.CLOSED:
                        connected_servers[add_to_req].close()
                        del connected_servers[add_to_req]
                        break

            except socket.gaierror:
                print('#######################################')
                print("there was an error resolving the host")

            if req.connection_type == constants.CLOSED:
                break

        c.close()

    def telnet(self):
        self.s_telnet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_telnet.bind((self.telnet_host, self.telnet_port))
        print("telnet server bound to port", self.telnet_port)

        self.s_telnet.listen(5)
        print("telnet server is listening")

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
            if char[len(char) - 1] != ';':
                command += char
            else:
                response = self.get_command_response(command)
                c.send(bytes('\r' + command + '\n\r' + response, 'utf-8'))
                if response.split('\n\r') == 'Bye':
                    c.close()
                    break
                command = ''

        c.close()

    def get_command_response(self, command: str) -> str:
        response = ''
        if command == 'packet length stats':
            response += 'Packet length received from server(mean, std): ('
            bigger_temp = self.connection_data['pls']
            temp = bigger_temp['ps']
            if len(temp) > 0:
                response += str(sum(temp) / len(temp)) + ', ' + str(np.std(np.array(temp))) + ')\n\r'
            else:
                response += '0, 0)\n\r'
            response += 'Packet length received from client(mean, std): ('
            temp = bigger_temp['pc']
            if len(temp) > 0:
                response += str(sum(temp) / len(temp)) + ', ' + str(np.std(np.array(temp))) + ')\n\r'
            else:
                response += '0, 0)\n\r'
            response += 'Body length received from server(mean, std): ('
            temp = bigger_temp['bs']
            if len(temp) > 0:
                response += str(sum(temp) / len(temp)) + ', ' + str(np.std(np.array(temp))) + ')\n\r'
            else:
                response += '0, 0)\n\r'

        elif command == 'status count':
            for code in constants.code_message:
                response += str(code) + ' ' + constants.code_message[code] + ': '
                response += str(self.connection_data['stat'][code])
                response += '\n\r'

        elif command == 'exit':
            response += 'Bye'

        elif command == 'type count':
            for types in constants.file_types:
                response += types + ': '
                response += str(self.connection_data['type'][constants.file_types[types]]) + '\n\r'

        elif command[:3] == 'top':
            temp = command.split(' ')
            k = int(temp[1])
            temp = self.connection_data['visited'].copy()
            temp = {k: v for k, v in sorted(temp.items(), key=lambda item: item[1])}
            temp_keys = list(temp.keys())
            if len(temp) > k:
                for i in range(k):
                    site = temp_keys[i].split(':')[0]
                    response += str(i + 1) + '. ' + site + '\n\r'
            else:
                for i in range(len(temp)):
                    site = temp_keys[i].split(':')[0]
                    response += str(i + 1) + '. ' + site + '\n\r'
        else:
            response += '400 Bad Request'

        response += '\n\r'
        return response

    @staticmethod
    def get_body_length(data: bytes) -> int:
        packet = str(data, 'utf-8').split('\r\n\r\n')
        body = packet[1]
        return len(body)

    @staticmethod
    def get_packet_type(data: bytes) -> str:
        packet = str(data, 'utf-8').split('\r\n')
        for line in packet:
            if line.split(': ')[0] == 'Content-Type':
                content_type = line.split(': ')[1].split(';')[0]
                if content_type in constants.file_types:
                    return constants.file_types[line.split(': ')[1].split(';')[0]]
                else:
                    return 'a'

    @staticmethod
    def get_packet_status(data: bytes) -> int:
        return int(str(data, 'utf-8').split('\r\n')[0].split(' ')[1])

    @staticmethod
    def get_packet_host(data: bytes) -> str:
        req = RequestPacket(str(data, 'utf-8'))
        req.set_main_address()
        return req.main_address

    def update_connection_data(self, packet: bytes, is_server: bool, cutoff=0):
        if is_server:
            self.connection_data['pls']['ps'].append(len(packet))
            if cutoff == 0:
                self.connection_data['pls']['bs'].append(self.get_body_length(packet))
            else:
                self.connection_data['pls']['bs'].append(len(packet) - cutoff)
            if cutoff > 0:
                packet = packet[:cutoff]
            if self.get_packet_type(packet) != 'a':
                self.connection_data['type'][self.get_packet_type(packet)] += 1
            code = self.get_packet_status(packet)
            if code in self.connection_data['stat']:
                self.connection_data['stat'][code] += 1

        else:
            self.connection_data['pls']['pc'].append(len(packet))
            host = self.get_packet_host(packet)
            if host in self.connection_data['visited']:
                self.connection_data['visited'][host] += 1
            else:
                self.connection_data['visited'][host] = 1


proxy = ProxyServer()
