class ConnectionTimeout(Exception):
    pass


class ReadTimeout(Exception):
    pass


class ResponseException(Exception):
    pass


class TransferEncodingException(ResponseException):
    pass


class ContentEncodingException(ResponseException):
    pass
