import asyncio
import collections

from . import (
    models,
    exc,
    uri,
    rfc2161)


class Protocol(object):
    HTTP_VERSION = 1.1


class Request(object):
    PROTOCOL = Protocol

    def __init__(self, method, url, headers=None):
        self.method = method
        self.url = url
        self.uri_reference = uri.from_string(url)

        path = self.uri_reference['path']
        if self.uri_reference.get('query'):
            path = '{}?{}'.format(path, self.uri_reference['query'])
        self.path = path

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.uri_reference['authority']

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

    async def connect(
        self,
        connection_timeout=None,
        loop=None,
    ):
        if self.uri_reference['scheme'] == 'https':
            port, ssl = 443, True
        else:
            port, ssl = 80, False

        conn = asyncio.open_connection(
            self.uri_reference['authority'],
            port,
            ssl=ssl,
            loop=loop,
        )
        try:
            reader, writer = await asyncio.wait_for(conn, connection_timeout)
        except asyncio.TimeoutError:
            raise exc.ConnectionTimeout
        writer.write(str(self).encode('latin-1'))
        socket = models.Socket(reader=reader, writer=writer)
        return models.Connection(
            self.url,
            socket,
            connection_timeout,
            3.,
        )
