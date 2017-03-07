import re

from . import utils


class RequestProtocol(object):
    METHOD_GET = 'GET'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_HEAD = 'HEAD'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'
    METHOD_TRACE = 'TRACE'
    METHOD_CONNECT = 'CONNECT'

    HTTP_VERSION = '1.1'

    CRLF = '\r\n'
    SP = ' '

    REQUEST_LINE = '{method}{sp}{request_uri}{sp}HTTP/{http_version}{crlf}'

    @classmethod
    def path(cls, uri):
        path = uri.path
        if uri.query:
            path = '{}?{}'.format(path, uri.query)
        return path

    @classmethod
    def header_fields(cls, headers):
        return '\r\n'.join(
            '{}: {}'.format(h, v) for h, v in headers.items())

    @classmethod
    def request_line(cls, method, request_uri):
        return cls.REQUEST_LINE.format(
            method=method,
            sp=cls.SP,
            request_uri=request_uri,
            http_version=cls.HTTP_VERSION,
            crlf=cls.CRLF)


class ResponseProtocol(object):
    COLON = ':'
    HTTP = 'HTTP/'

    REGEX_CHARSET = re.compile(r';\s*charset=([^;]*)', re.I)
    REGEX_TOKEN = re.compile(
        r'([a-zA-Z][a-zA-Z_-]*)\s*(?:=(?:"([^"]*)"|'
        r'([^ \t",;]*)))?')

    @classmethod
    def parse_status(cls, status):
        if status.startswith(cls.HTTP):
            http_version, status_code, status_text = status.split(None, 2)
            status = '{} {}'.format(
                utils.smart_text(status_code),
                utils.smart_text(status_text))
        return status

    @classmethod
    def parse_status_code(cls, status):
        return int(status.split()[0])

    @classmethod
    def parse_charset(cls, header, charset):
        match = cls.REGEX_CHARSET.search(utils.smart_text(header))
        if match:
            charset = match.group(1)
        return charset

    @classmethod
    def parse_cache_control(cls, header):
        header = utils.smart_text(header)
        cache = {}
        for match in cls.REGEX_TOKEN.finditer(header):
            name = match.group(1)
            value = match.group(2) or match.group(3) or None
            if value and value.isdigit():
                value = int(value)
            cache[name] = value

        cache_control = {}
        for n in [
            'public',
            'no-store',
            'no-transform',
            'must-revalidate',
            'proxy-revalidate',
        ]:
            if n not in cache:
                continue
            cache_control[n] = None

        for n, v in cache.items():
            if n not in [
                'private',
                'no-cache',
                'max-age',
                's-maxage',
                'stale-while-revalidate',
                'stale-if-error',
            ]:
                continue
            cache_control[n] = v
        return cache_control
