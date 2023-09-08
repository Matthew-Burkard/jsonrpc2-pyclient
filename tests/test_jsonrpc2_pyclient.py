"""Client unit tests."""
import asyncio
import unittest
from dataclasses import dataclass

from jsonrpc2pyclient.httpclient import AsyncRPCHTTPClient, RPCHTTPClient

# FIXME These tests need to stand alone.
#  Use some sort of mock server.


@dataclass
class Vector3:
    """Basic test model."""

    x: float
    y: float
    z: float


class AsyncMathClient(AsyncRPCHTTPClient):
    """Test implementation of AsyncRPCHTTPClient."""

    async def add(self, a: float, b: float) -> float:
        """Basic test function."""
        return await self.call("math.add", [a, b])

    async def get_distance(self, target: Vector3, other: Vector3) -> Vector3:
        """Test function with models."""
        return Vector3(**await self.call("math.get_distance", [target, other]))


class MathClient(RPCHTTPClient):
    """Test implementation of RPCHTTPClient."""

    def add(self, a: float, b: float) -> float:
        """Basic test function."""
        return self.call("math.add", [a, b])

    def get_distance(self, target: Vector3, other: Vector3) -> Vector3:
        """Test function with models."""
        return Vector3(**self.call("math.get_distance", [target, other]))


class AsyncRPCClientTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        self.client = AsyncMathClient("http://localhost:8000/api/v1")
        super(AsyncRPCClientTest, self).__init__(*args)

    def test_basic_func(self) -> None:
        self.assertEqual(4, asyncio.run(self.client.add(2, 2)))

    def test_model_func(self) -> None:
        self.assertEqual(
            Vector3(1, 1, 1),
            asyncio.run(self.client.get_distance(Vector3(2, 2, 2), Vector3(1, 1, 1))),
        )


class RPCClientTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        self.client = MathClient("http://localhost:8000/api/v1")
        super(RPCClientTest, self).__init__(*args)

    def test_basic_func(self) -> None:
        self.assertEqual(4, self.client.add(2, 2))

    def test_model_func(self) -> None:
        self.assertEqual(
            Vector3(1, 1, 1),
            self.client.get_distance(Vector3(2, 2, 2), Vector3(1, 1, 1)),
        )
