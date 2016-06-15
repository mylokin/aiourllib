class Request(object):
    CRLF = b'\r\n'
    SP = b' '

    METHOD_GET = 'GET'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_HEAD = 'HEAD'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'
    METHOD_TRACE = 'TRACE'
    METHOD_CONNECT = 'CONNECT'

    METHOD = [
        METHOD_GET,
        METHOD_OPTIONS,
        METHOD_HEAD,
        METHOD_POST,
        METHOD_PUT,
        METHOD_DELETE,
        METHOD_TRACE,
        METHOD_CONNECT,
    ]

    @classmethod
    def method_exists(cls, method):
        return method in cls.METHOD

    @classmethod
    def request_line(cls, method, request_uri, http_version):
        return b'{method}{SP}{request_uri}{SP}{http_version}{CRLF}'.format(
            method=method,
            request_uri=request_uri,
            http_version=http_version,
            SP=cls.SP,
            CRLF=cls.CRLF)
