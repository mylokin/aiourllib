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
    request = Request(
        Request.PROTOCOL.METHOD_GET,
        uri_reference,
        headers=headers)
    response = await request.connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )
    return response


async def head(
    uri_reference,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    request = Request(
        Request.PROTOCOL.METHOD_HEAD,
        uri_reference,
        headers=headers)
    response = await request.connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )
    return response


async def post(
    uri_reference,
    data,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    request = Request(
        Request.PROTOCOL.METHOD_POST,
        uri_reference,
        data=data,
        headers=headers,
    )
    response = await request.connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )

    return response
