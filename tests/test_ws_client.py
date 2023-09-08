"""WebSocket Client unit tests."""
import asyncio
import datetime

import pytest
from jsonrpcobjects.errors import ServerError

from jsonrpc2pyclient.wsclient import AsyncRPCWSClient

client = AsyncRPCWSClient("ws://localhost:8000/api/v1")


@pytest.mark.asyncio
async def test_async() -> None:
    await client.connect()
    start = datetime.datetime.now()
    res = await asyncio.gather(client.call("wait", [1.0]), client.call("wait", [0.8]))
    assert res == [1.0, 0.8]
    assert datetime.datetime.now() - start < datetime.timedelta(seconds=1.5)
    await client.close()


@pytest.mark.asyncio
async def test_async_error() -> None:
    await client.connect()
    start = datetime.datetime.now()
    with pytest.raises(ServerError):
        await client.call("math.divide", [0, 0])
    assert datetime.datetime.now() - start < datetime.timedelta(seconds=0.1)
    await client.close()


@pytest.mark.asyncio
async def test_async_error() -> None:
    async with client as open_client:
        start = datetime.datetime.now()
        with pytest.raises(ServerError):
            await open_client.call("math.divide", [0, 0])
        assert datetime.datetime.now() - start < datetime.timedelta(seconds=0.1)
