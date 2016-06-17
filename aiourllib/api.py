import asyncio
import urllib.parse

from . import models
from .response import Response
from .request import Request


async def read(connection):
    response = Response(connection)
    await response.read_headers()
    return response


async def connect(url, loop=None):
    pr = urllib.parse.urlsplit(url)
    if pr.scheme == 'https':
        port, ssl = 443, True
    else:
        port, ssl = 80, False

    conn = asyncio.open_connection(
        pr.hostname,
        port,
        ssl=ssl,
        loop=loop,
    )
    reader, writer = await conn
    return models.Connection(url, reader, writer)


async def get(url, headers=None, loop=None):
    conn = await connect(url, loop=loop)

    request = str(Request('get', url, headers=headers)).encode('latin-1')
    conn.writer.write(request)

    return (await read(conn))
