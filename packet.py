from constants import *
import datetime


class RequestPacket:
    def __init__(self, string: str):
        self.string: str = string
        self.request_method: str = ''
        self.request_address: str = ''
        self.request_version: str = ''
        self.connection_type: int = CLOSED
        self.encoding: list = []
        self.timer: int = 60
        self.can_gzip: bool = False
        self.code = self.set_values()
        self.code_msg = code_message[self.code]
        self.html_file = None
        self.file_type = None

    def set_values(self):
        lines = self.string.split('\r\n')
        request_line = lines[0].split(' ')
        if len(request_line) != 3:
            return 400
        temp_lines = []
        for i in range(1, len(lines)):
            if lines[i] == '':
                continue
            if len(lines[i].split(': ')) != 2:
                print('here', len(lines[i]))
                return 400
            temp_lines.append(lines[i].split('\r')[0])
        lines = temp_lines
        self.request_method = request_line[0]
        self.request_address = request_line[1]
        self.request_version = request_line[2]
        if self.request_method not in standard_methods:
            return 501
        if self.request_method != 'GET':
            return 405
        for line in lines:
            if line == '':
                continue
            header_name = line.split(': ')[0]
            header_value = line.split(': ')[1]
            if header_name == 'Connection':
                if header_value == 'keep-alive':
                    self.connection_type = KEEP_ALIVE_CONNECTION
                elif header_value == 'close':
                    self.connection_type = CLOSED
            elif header_name == 'Keep-Alive':
                self.timer = int(header_value)
            elif header_name == 'Accept-Encoding':
                encodings = header_value.split(', ')
                if 'text/html' in encodings:
                    self.encoding.append(TEXT_HTML_ENCODING)
                if 'text/plain' in encodings:
                    self.encoding.append(TEXT_PLAIN_ENCODING)
                if 'image/jpg' in encodings:
                    self.encoding.append(IMG_JPG_ENCODING)
                if 'image/jpeg' in encodings:
                    self.encoding.append(IMG_JPEG_ENCODING)
                if 'image/png' in encodings:
                    self.encoding.append(IMG_PNG_ENCODING)
                if 'gzip' in encodings:
                    self.can_gzip = True
                    self.encoding.append(GZIP_ENCODING)
        return 200

    def request_string(self) -> str:
        return ' '.join([self.request_method, self.request_address, self.request_version.split('\r')[0]])

    def log(self) -> str:
        log = ''
        log += '[' + ResponsePacket.get_date() + '] '
        log += '\"' + self.request_string() + '\" '
        log += '\"' + str(self.code) + ' ' + code_message[self.code] + '\"'
        return log

    def set_file(self, html_file=None, file_type=None):
        if html_file:
            self.html_file = html_file
            self.file_type = file_type
        else:
            self.code = 404


class ResponsePacket:
    def __init__(self, request: RequestPacket):
        self.request_packet: RequestPacket = request
        self.message: bytes = self.create_response()
        pass

    def create_response(self) -> bytes:
        code = self.request_packet.code
        message = ''
        if code == 200:
            message += self.request_packet.request_version + ' ' + str(code) + ' ' + code_message[code] + '\n'
            message += 'Connection: close\n'
            message += 'Content-Length: ' + str(len(self.request_packet.html_file)) + '\n'
            message += 'Content-Type: ' + self.request_packet.file_type + '\n'
            message += 'Date: ' + self.get_date() + '\n'
            message += '\n'
            if type(self.request_packet.html_file) == str:
                message += self.request_packet.html_file
                message_bytes = bytes(message, 'utf-8')
            else:
                message_bytes = bytes(message, 'utf-8')
                message_bytes += self.request_packet.html_file

        else:
            mes_to_send='<!DOCTYPE html>\n<html>\n<body>\n<h1>' + error_message[code] + '</h1>\n</body>\n</html>\n'
            message += self.request_packet.request_version + ' ' + str(code) + ' ' + code_message[code] + '\n'
            message += 'Connection: close\n'
            message += 'Content-Length: ' + str(len(mes_to_send)) + '\n'
            message += 'Content-Type: text/html\n'
            if code == 405:
                message += 'Allow: GET\n'
            message += 'Date: ' + self.get_date() + '\n'
            message += '\n'
            message += mes_to_send
            message_bytes = bytes(message, 'utf-8')
            print('##############################'+error_message[code])
        return message_bytes

    @staticmethod
    def get_date() -> str:
        date = datetime.datetime.utcnow()
        weekday = day_of_week[date.weekday()] + ', '
        day = str(date.day) + ' '
        month = months[date.month] + ' '
        year = str(date.year) + ' '
        hour = str(date.hour) + ':'
        minute = str(date.minute) + ':'
        second = str(date.second) + ' '
        time_zone = 'GMT'
        return weekday + day + month + year + hour + minute + second + time_zone
