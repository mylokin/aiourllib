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

    def __init__(self, method, uri_reference, data=None, headers=None):
        self.method = method
        self.data = data

        self.uri_reference = uri_reference
        self.uri = uri.from_string(uri_reference)

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.uri.authority

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
            reader, writer = await asyncio.wait_for(
                conn, connection_timeout, loop=loop)
        except asyncio.TimeoutError:
            raise exc.ConnectionTimeout
        writer.write(str(self).encode('latin-1'))
        socket_pair = models.SocketPair(reader=reader, writer=writer)
        return Response(models.Connection(
            self.uri_reference,
            socket_pair,
            connection_timeout,
            3.,
        ))
