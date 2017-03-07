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


class URIException(Exception):
    pass


class SchemeException(URIException):
    pass


class UserInfoException(URIException):
    pass


class PortException(URIException):
    pass


class AuthorityException(URIException):
    pass


class FragmentException(URIException):
    pass


class QueryException(URIException):
    pass


class PathException(URIException):
    pass
