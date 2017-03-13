import asyncio
import collections
import json
import gzip
import zlib

from . import (
    exc,
    protocol,
    utils)


class AbstractResponse(object):
    @property
    def status_code(self):
        if not self._status_code:
            self._status_code = self.PROTOCOL.parse_status_code(self.status)
        return self._status_code

    @property
    def content_length(self):
        if (not self._content_length) and self.has_header('Content-Length'):
            self._content_length = int(self.get_header('Content-Length'))
        return self._content_length

    @property
    def content_type(self):
        if (not self._content_type) and self.has_header('Content-Type'):
            self._content_type = \
                utils.smart_text(self.get_header('Content-Type'))
        return self._content_type

    @property
    def content_encoding(self):
        if not self._content_encoding:
            if self.has_header('Content-Encoding'):
                self._content_encoding = \
                    utils.smart_text(self.get_header('Content-Encoding'))
            else:
                self._content_encoding = 'identity'
        return self._content_encoding

    @property
    def transfer_encoding(self):
        if not self._transfer_encoding:
            if self.has_header('Transfer-Encoding'):
                self._transfer_encoding = \
                    utils.smart_text(self.get_header('Transfer-Encoding'))
            else:
                self._transfer_encoding = 'identity'
        return self._transfer_encoding

    @property
    def charset(self):
        if (not self._charset) and self.content_type:
            self._charset = self.PROTOCOL.parse_charset(
                self.content_type, self._charset)
        return self._charset

    @property
    def cache_control(self):
        if (not self._cache_control) and self.has_header('Cache-Control'):
            self._cache_control = self.PROTOCOL.parse_cache_control(
                self.get_header('Cache-Control'))
        return self._cache_control


class Response(AbstractResponse):
    PROTOCOL = protocol.ResponseProtocol

    CONTENT_TYPE = 'text/html'
    CHARSET = 'UTF-8'

    def __init__(self, connection):
        self.connection = connection

        self.status = None
        self.headers = None

        self._status_code = None
        self._content_encoding = None
        self._content_length = None
        self._content_type = self.CONTENT_TYPE
        self._charset = self.CHARSET
        self._cache_control = None
        self._transfer_encoding = None

        self._content = None

    def get_header(self, header):
        mapping = {h.lower(): h for h in self.headers}
        header = header.lower()
        if header in mapping:
            return self.headers[mapping[header]]

    def has_header(self, header):
        mapping = {h.lower(): h for h in self.headers}
        header = header.lower()
        return header in mapping

    async def read_headers(self):
        status = (await self.connection.readline()).strip()

        status = utils.smart_text(status, 'latin-1')
        self.status = self.PROTOCOL.parse_status(status)

        self.headers = collections.OrderedDict()
        while True:
            line = (await self.connection.readline()).strip()
            line = utils.smart_text(line, 'latin-1')
            if not line:
                break

            try:
                header, value = line.split(self.PROTOCOL.COLON, 1)
            except ValueError:
                raise ValueError('Bad header line: {}'.format(
                    utils.smart_text(line)))

            header = utils.smart_text(header.strip(), 'latin-1')
            value = utils.smart_text(value.strip(), 'latin-1')
            self.headers[header] = value

    def read(self):
        if self.transfer_encoding == 'chunked':
            return self.connection.read_chunks()
        elif self.transfer_encoding == 'deflate':
            return self.connection.read_deflate(self.content_length)
        elif self.transfer_encoding == 'gzip':
            return self.connection.read_gzip(self.content_length)
        elif self.transfer_encoding == 'identity':
            return self.connection.read_identity(self.content_length)
        else:
            raise exc.TransferEncodingException(self.transfer_encoding)

    async def read_content(self):
        if not self._content:
            content = await self.read()
            if self.content_encoding == 'deflate':
                content = zlib.decompress(content)
            elif self.content_encoding == 'gzip':
                content = gzip.decompress(content)
            elif self.content_encoding == 'identity':
                pass
            else:
                raise exc.ContentEncodingException(self.content_encoding)
            self._content = content
        return self._content

    async def read_text(self):
        content = await self.read_content()
        return content.decode(self.charset)

    async def read_json(self):
        content = await self.read_text()
        return json.loads(content)

    def close(self):
        self.connection.socket_pair.writer.close()
