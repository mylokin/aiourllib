import asyncio
import collections
import functools
import operator

from . import (
    models,
    exc,
    protocol,
    uri,
    utils)
from .response import Response


class Request(object):
    PROTOCOL = protocol.RequestProtocol

    def __init__(
        self,
        method,
        uri_reference,
        data=None,
        data_encoding='utf-8',
        headers=None,
    ):
        self.method = method
        self.data = data and str(data).encode(data_encoding)

        self.uri_reference = uri_reference
        self.uri = uri.from_string(uri_reference)

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.uri.authority

        if self.data:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            self.headers['Content-Length'] = len(data)

    def __str__(self):
        request_line = self.PROTOCOL.request_line(
            self.method,
            self.PROTOCOL.path(self.uri))
        return (
            '{request_line}'
            '{header_fields}\r\n'
            '\r\n'.format(
                request_line=request_line,
                header_fields=self.PROTOCOL.header_fields(self.headers)))

    async def connect(
        self,
        connection_timeout=None,
        read_timeout=None,
        loop=None,
    ):
        if self.uri.scheme == 'https':
            port, ssl = 443, True
        else:
            port, ssl = 80, False

        connection = models.Connection(
            connection_timeout, read_timeout, loop=loop)

        socket_pair = await connection.connect(self.uri.authority, port, ssl)

        request_line = str(self).encode('latin-1')
        socket_pair.writer.write(request_line)

        if self.data:
            socket_pair.writer.write(self.data)
            socket_pair.writer.write(b'\r\n')

        if socket_pair.writer.can_write_eof():
            socket_pair.writer.write_eof()

        response = Response(connection)
        await response.read_headers()

        return response
