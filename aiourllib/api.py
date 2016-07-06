import asyncio

from . import (
    exc,
    models,
    uri)
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
    uri_reference = uri.from_string(url)
    if uri_reference['scheme'] == 'https':
        port, ssl = 443, True
    else:
        port, ssl = 80, False

    conn = asyncio.open_connection(
        uri_reference['authority'],
        port,
        ssl=ssl,
        loop=loop,
    )
    try:
        reader, writer = await asyncio.wait_for(conn, connection_timeout)
    except asyncio.TimeoutError:
        raise exc.ConnectionTimeout
    else:
        socket = models.Socket(reader=reader, writer=writer)

    return models.Connection(
        url,
        socket,
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
    conn.socket.writer.write(request)

    return (await read(conn))
