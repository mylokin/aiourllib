import asyncio
import collections
import gzip
import zlib

from . import exc


class Connection(object):
    def __init__(self, connection_timeout, read_timeout, loop=None):
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.loop = loop

        self.socket_pair = None

    async def read_coro(self, coro):
        try:
            return await asyncio.wait_for(coro, self.read_timeout)
        except asyncio.TimeoutError:
            raise exc.ReadTimeout

    async def read(self, chunk_size):
        coro = self.socket_pair.reader.read(chunk_size)
        return (await self.read_coro(coro))

    async def readexactly(self, chunk_size):
        coro = self.socket_pair.reader.readexactly(chunk_size)
        return (await self.read_coro(coro))

    async def readline(self):
        coro = self.socket_pair.reader.readline()
        return (await self.read_coro(coro))

    async def read_chunks(self):
        content = b''
        while True:
            chunk_size = (await self.readline()).strip()
            if not chunk_size:
                break

            chunk_size = int(chunk_size, base=16)
            r = await self.readexactly(chunk_size)
            if not r:
                break

            content += r
            await self.readline()

        return content

    async def read_identity(self, content_length):
        content = b''
        while len(content) < content_length:
            chunk_size = content_length - len(content)

            r = await self.read(chunk_size)

            if r:
                content += r
            else:
                break
        return content

    async def read_deflate(self, content_length):
        return zlib.decompress(await self.read_identity(content_length))

    async def read_gzip(self, content_length):
        return gzip.decompress(await self.read_identity(content_length))

    async def connect(self, authority, port, ssl=False):
        conn = asyncio.open_connection(
            authority,
            port,
            ssl=ssl,
            loop=self.loop)

        try:
            reader, writer = await asyncio.wait_for(
                conn, self.connection_timeout, loop=self.loop)
        except asyncio.TimeoutError:
            raise exc.ConnectionTimeout

        self.socket_pair = SocketPair(reader=reader, writer=writer)
        return self.socket_pair


SocketPair = collections.namedtuple('SocketPair', [
    'reader',
    'writer',
])


URI = collections.namedtuple('URI', [
    'scheme',
    'authority',
    'path',
    'query',
    'fragment',
    'components',
])


URIComponents = collections.namedtuple('URIComponents', [
    'userinfo',
    'port',
    'host',
    'ipv6_address',
    'ipv4_address',
    'reg_name',
    'path_abempty',
    'path_absolute',
    'path_rootless',
    'path_empty',
    'relative_ref',
])
