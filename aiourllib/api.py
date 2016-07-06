import asyncio

from . import (
    exc,
    models,
    uri)
from .response import Response
from .request import Request


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
    response = await request.connect()
    await response.read_headers()
    return response
