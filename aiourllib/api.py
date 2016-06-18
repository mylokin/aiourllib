import asyncio
import urllib.parse

from . import (
    exc,
    models)
from .response import Response
from .request import Request


async def read(connection):
    response = Response(connection)
    await response.read_headers()
    return response


async def connect(
    url,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
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
    try:
        reader, writer = await asyncio.wait_for(conn, connection_timeout)
    except asyncio.TimeoutError:
        raise exc.ConnectionTimeout

    return models.Connection(
        url,
        reader,
        writer,
        connection_timeout,
        read_timeout,
    )


async def get(
    url,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    conn = await connect(
        url,
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop)
    request = Request(
        'get',
        url,
        headers=headers)
    request = str(request).encode('latin-1')
    conn.writer.write(request)

    return (await read(conn))
