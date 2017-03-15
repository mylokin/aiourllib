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
    return await Request(
        Request.PROTOCOL.METHOD_GET,
        uri_reference,
        headers=headers,
    ).connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )


async def head(
    uri_reference,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    return await Request(
        Request.PROTOCOL.METHOD_HEAD,
        uri_reference,
        headers=headers,
    ).connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )


async def post(
    uri_reference,
    data,
    headers=None,
    connection_timeout=None,
    read_timeout=None,
    loop=None,
):
    return await Request(
        Request.PROTOCOL.METHOD_POST,
        uri_reference,
        data=data,
        headers=headers,
    ).connect(
        connection_timeout=connection_timeout,
        read_timeout=read_timeout,
        loop=loop,
    )
