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


class Request(object):
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

    def __init__(self, method, uri_reference, headers=None):
        self.method = method
        self.uri_reference = uri_reference
        self.uri = uri.from_string(uri_reference)

        self.headers = collections.OrderedDict(headers or [])
        self.headers['Host'] = self.uri.authority

    @classmethod
    def request_line(cls, method, request_uri):
        return cls.REQUEST_LINE.format(
            method=method,
            sp=cls.SP,
            request_uri=request_uri,
            http_version=cls.HTTP_VERSION,
            crlf=cls.CRLF)

    @property
    def path(self):
        path = self.uri.path
        if self.uri.query:
            path = '{}?{}'.format(path, self.uri.query)
        return path

    @property
    def line(self):
        return self.request_line(
            self.method,
            self.path).decode('utf-8')

    @property
    def header_fields(self):
        return '\r\n'.join(
            '{}: {}'.format(h, v) for h, v in self.headers.items())

    def __str__(self):
        request_line = self.request_line(
            self.method,
            self.path,
        )
        return (
            '{request_line}'
            '{header_fields}\r\n'
            '\r\n'.format(
                request_line=request_line,
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
            reader, writer = await asyncio.wait_for(
                conn, connection_timeout, loop=loop)
        except asyncio.TimeoutError:
            raise exc.ConnectionTimeout
        writer.write(str(self).encode('latin-1'))
        socket = models.Socket(reader=reader, writer=writer)
        return Response(models.Connection(
            self.uri_reference,
            socket,
            connection_timeout,
            3.,
        ))
