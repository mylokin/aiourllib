import asyncio
import collections
import re

from . import utils


class Response(object):
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
        self._content_length = None
        self._content_type = self.CONTENT_TYPE
        self._charset = self.CHARSET
        self._cache_control = None

        self._content = None

    @property
    def status_code(self):
        if not self._status_code:
            self._status_code = Protocol.parse_status_code(self.status)
        return self._status_code

    @property
    def content_length(self):
        if (not self._content_length) and ('Content-Length' in self.headers):
            self._content_length = int(self.headers['Content-Length'])
        return self._content_length

    @property
    def content_type(self):
        if (not self._content_type) and ('Content-Type' in self.headers):
            self._content_type = utils.smart_text(self.headers['Content-Type'])
        return self._content_type

    @property
    def charset(self):
        if (not self._charset) and self.content_type:
            self._charset = Protocol.parse_charset(self.content_type, self._charset)
        return self._charset

    @property
    def cache_control(self):
        if (not self._cache_control) and ('Cache-Control' in self.headers):
            self._cache_control = Protocol.parse_cache_control(self.headers['Cache-Control'])
        return self._cache_control

    async def read_headers(self):
        status = (await self.reader.readline()).strip()
        status = utils.smart_text(status, 'latin-1')
        self.status = Protocol.parse_status(status)

        self.headers = collections.OrderedDict()
        while True:
            line = (await self.reader.readline()).strip()
            line = utils.smart_text(line, 'latin-1')
            if not line:
                break

            try:
                header, value = line.split(Protocol.COLON, 1)
            except ValueError:
                raise ValueError('Bad header line: {}'.format(utils.smart_text(line)))

            header = utils.smart_text(header.strip(), 'latin-1')
            value = utils.smart_text(value.strip(), 'latin-1')
            self.headers[header] = value

    async def read_chunks(self):
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
            if self.content_length:
                self._content = await self.read_chunks()
            else:
                self._content = await self.reader.read()
        return self._content

    async def read_text(self):
        content = await self.read_content()
        return content.decode(self.charset)

    def close(self):
        self.writer.close()


class Protocol(object):
    COLON = ':'
    HTTP = 'HTTP/'

    REGEX_CHARSET = re.compile(r';\s*charset=([^;]*)', re.I)
    REGEX_TOKEN = re.compile(r'([a-zA-Z][a-zA-Z_-]*)\s*(?:=(?:"([^"]*)"|([^ \t",;]*)))?')

    @classmethod
    def parse_status(cls, status):
        if status.startswith(cls.HTTP):
            http_version, status_code, status_text = status.split(None, 2)
            status = '{} {}'.format(utils.smart_text(status_code), utils.smart_text(status_text))
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
