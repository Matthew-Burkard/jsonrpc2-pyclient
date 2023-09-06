"""WebSocket Client unit tests."""
import asyncio
import datetime

import pytest

from jsonrpc2pyclient.wsclient import AsyncRPCWSClient


@pytest.mark.asyncio
async def test_async() -> None:
    client = AsyncRPCWSClient("ws://localhost:8000/api/v1")
    await client.connect()
    start = datetime.datetime.now()
    res = await asyncio.gather(client.call("wait", [1.0]), client.call("wait", [0.8]))
    assert res == [1.0, 0.8]
    assert datetime.datetime.now() - start < datetime.timedelta(seconds=1.5)
    await client.close()
