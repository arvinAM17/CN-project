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

    def set_values(self):
        lines = self.string.split('\n')
        request_line = lines[0].split()
        if len(request_line) != 3:
            return 400
        for i in range(1, len(lines)):
            if lines[i] == '':
                continue
            if len(lines[i].split(': ')) != 2:
                return 400
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
        return ' '.join([self.request_method, self.request_address, self.request_version])

    def log(self) -> str:
        log = '[' + ResponsePacket.get_date() + '] '
        log += '"' + self.request_string() + '" '
        log += '"' + '"' + str(self.code) + ' ' + code_message[self.code] + '"\n'
        return log


class ResponsePacket:
    def __init__(self, request: RequestPacket):
        self.request_packet: RequestPacket = request
        self.message: str = self.create_response()
        pass

    def create_response(self) -> str:
        code = self.request_packet.code
        message = ''
        if code == 200:
            pass
        if code == 404:
            pass
        else:
            message += self.request_packet.request_version + str(code) + code_message[code] + '\n'
            message += 'Connection: close\n'
            message += 'Content-Length: ' + str(len(error_message[code])) + '\n'
            message += 'Content-Type: text/html\n'
            if code == 405:
                message += 'Allow: GET\n'
            message += 'Date: ' + self.get_date() + '\n'
            message += '\n'
            message += error_message[code] + '\n'
        return message

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
