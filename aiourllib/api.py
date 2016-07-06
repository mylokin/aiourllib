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


async def get(
    url,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    request = Request(
        'get',
        url,
        headers=headers)
    conn = await request.connect()
    return (await read(conn))
