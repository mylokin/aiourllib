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

    def __init__(self, method, uri_reference, headers=None):
        self.method = method
        self.uri_reference = uri_reference
        self.uri = uri.from_string(uri_reference)

        path = self.uri.path
        if self.uri.query:
            path = '{}?{}'.format(path, self.uri.query)
        self.path = path

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.uri.authority

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
        if self.uri.scheme == 'https':
            port, ssl = 443, True
        else:
            port, ssl = 80, False

        conn = asyncio.open_connection(
            self.uri.authority,
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
            self.uri_reference,
            socket,
            connection_timeout,
            3.,
        )
