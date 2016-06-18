import asyncio
import collections
import json
import re
import zlib

from . import utils


class Protocol(object):
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


class Response(object):
    PROTOCOL = Protocol

    CONTENT_TYPE = 'text/html'
    CHARSET = 'UTF-8'

    def __init__(
        self,
        connection,
        status=None,
        headers=None,
    ):
        self.reader = connection.reader
        self.writer = connection.writer

        self.status = status
        self.headers = headers

        self._status_code = None
        self._content_encoding = None
        self._content_length = None
        self._content_type = self.CONTENT_TYPE
        self._charset = self.CHARSET
        self._cache_control = None
        self._transfer_encoding = None

        self._content = None

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
        if (not self._content_encoding):
            if self.has_header('Content-Encoding'):
                self._content_encoding = \
                    utils.smart_text(self.get_header('Content-Encoding'))
            else:
                self._content_encoding = 'identity'
        return self._content_encoding

    @property
    def transfer_encoding(self):
        if (
            (not self._transfer_encoding) and
            self.has_header('Transfer-Encoding')
        ):
            self._transfer_encoding = \
                utils.smart_text(self.get_header('Transfer-Encoding'))
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
        status = (await self.reader.readline()).strip()
        status = utils.smart_text(status, 'latin-1')
        self.status = self.PROTOCOL.parse_status(status)

        self.headers = collections.OrderedDict()
        while True:
            line = (await self.reader.readline()).strip()
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
            return self.read_chunks()
        elif self.transfer_encoding == 'deflate':
            return self.read_deflate()
        else:
            return self.read_identity()

    async def read_chunks(self):
        content = b''
        while True:
            chunk_size = await self.reader.readline()
            chunk_size = chunk_size.strip()
            if not chunk_size:
                break

            chunk_size = int(chunk_size, base=16)
            r = await self.reader.readexactly(chunk_size)
            if not r:
                break

            content += r
            await self.reader.readline()

        return content

    async def read_deflate(self):
        content = await self.read_default()
        return zlib.decompress(content)

    async def read_identity(self):
        content = b''
        while len(content) < self.content_length:
            r = (await self.reader.read(self.content_length - len(content)))
            if r:
                content += r
            else:
                break
        return content

    async def read_content(self):
        if not self._content:
            content = await self.read()
            if self.content_encoding == 'deflate':
                content = zlib.decompress(content)
            self._content = content
        return self._content

    async def read_text(self):
        content = await self.read_content()
        return content.decode(self.charset)

    async def read_json(self):
        content = await self.read_text()
        return json.loads(content)

    def close(self):
        self.writer.close()
