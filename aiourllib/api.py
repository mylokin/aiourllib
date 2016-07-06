import asyncio

from . import (
    exc,
    models,
    uri)
from .response import Response
from .request import Request


async def get(
    uri_reference,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    request = Request(Request.METHOD_GET, uri_reference, headers=headers)
    response = await request.connect(
        connection_timeout=connection_timeout,
        loop=loop,
    )
    await response.read_headers()
    return response


async def head(
    uri_reference,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    request = Request(Request.METHOD_HEAD, uri_reference, headers=headers)
    response = await request.connect(
        connection_timeout=connection_timeout,
        loop=loop,
    )
    await asyncio.wait_for(
        response.read_headers(),
        read_timeout,
        loop=loop)
    return response
