TEXT_HTML_ENCODING = 0
TEXT_PLAIN_ENCODING = 1
IMG_JPG_ENCODING = 2
IMG_JPEG_ENCODING = 3
IMG_PNG_ENCODING = 4
GZIP_ENCODING = 5

KEEP_ALIVE_CONNECTION = 0
CLOSED = 1

code_message = {
    200: 'OK',
    400: 'Bad Request',
    501: 'Not Implemented',
    405: 'Method Not Allowed',
    404: 'Not Found',
}

standard_methods = ['GET', 'DELETE', 'HEAD', 'POST', 'PUT']

error_message = {
    400: 'Request message not in the right format.',
    501: 'This request method is not implemented.',
    405: 'This request method is not allowed',
    404: 'The requested file is not found',
}

months = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

day_of_week = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wen',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun',
}
