import asyncio
import urllib.parse

import webob

from . import models
from .response import Response

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


async def get(url, loop=None):
    conn = await connect(url, loop=loop)

    pr = urllib.parse.urlsplit(url)
    request = webob.Request.blank(pr.path or '/', base_url=url)
    headers = '{}\r\n\r\n'.format(str(request)).encode('latin-1')
    conn.writer.write(headers)

    return (await read(conn))
