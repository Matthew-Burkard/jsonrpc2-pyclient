"""Test client decorator."""
import pytest

from jsonrpc2pyclient.decorator import rpc_client
from jsonrpc2pyclient.wsclient import AsyncRPCWSClient

transport = AsyncRPCWSClient("ws://localhost:8000/api/v1")


@rpc_client(transport=transport)
class TestClient:
    @rpc_client(transport=transport, method_prefix="math.")
    class MathClient:
        async def add(self, a: int, b: int) -> int:
            ...

    math = MathClient()

    @staticmethod
    async def connect() -> None:
        """Connect to WebSocket server."""
        await transport.connect()

    @staticmethod
    async def close() -> None:
        """Close connection to WebSocket server."""
        await transport.close()


@pytest.mark.asyncio
async def test_decorator_client() -> None:
    client = TestClient()
    await client.connect()
    assert await client.math.add(2, 2) == 4
    await client.close()
