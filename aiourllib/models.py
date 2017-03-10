import asyncio
import collections

from . import exc


class Connection(object):
    def __init__(self, url, socket_pair, connection_timeout, read_timeout):
        self.url = url
        self.socket_pair = socket_pair
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout

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
