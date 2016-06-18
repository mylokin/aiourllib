import collections

from . import (
    uri,
    rfc2161)


class Protocol(object):
    HTTP_VERSION = 1.1


class Request(object):
    PROTOCOL = Protocol

    def __init__(self, method, url, headers=None):
        self.method = method
        self.url = uri.URIFabric.from_string(url)

        path = self.url.abs_path
        if self.url.query:
            path = '{}?{}'.format(path, self.url.query)
        self.path = path

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.url.hostport

    @property
    def line(self):
        return '{method} {path} HTTP/{http_version}'.format(
            method=self.method.upper(),
            path=self.path,
            http_version=self.PROTOCOL.HTTP_VERSION)

    @property
    def header_fields(self):
        return '\r\n'.join(
            '{}: {}'.format(h, v) for h, v in self.headers.items())

    def __str__(self):
        return (
            '{line}\r\n'
            '{header_fields}\r\n'
            '\r\n'.format(
                line=self.line,
                header_fields=self.header_fields))
