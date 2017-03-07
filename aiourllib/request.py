import asyncio
import collections
import functools
import operator

from . import (
    models,
    exc,
    uri,
    utils)
from .response import Response


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


class Request(object):
    PROTOCOL = RequestProtocol

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
