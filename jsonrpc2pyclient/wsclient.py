"""RPCClient Websocket implementation."""
__all__ = ("AsyncRPCWSClient",)

import asyncio
import json
from types import TracebackType
from typing import Any, Optional, Union

from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedOK

from jsonrpc2pyclient.rpcclient import AsyncRPCClient


class AsyncRPCWSClient(AsyncRPCClient):
    """A JSON-RPC async Websocket Client."""

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None) -> None:
        """Init async WS client with URL and headers."""
        self.headers = headers
        self.url = url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self._message_resolvers: dict[int, asyncio.Event] = {}
        self._responses: dict[int, str] = {}
        super(AsyncRPCWSClient, self).__init__()

    async def __aenter__(self) -> "AsyncRPCWSClient":
        """Open WebSocket connection."""
        self.websocket = await connect(self.url, extra_headers=self.headers)
        asyncio.create_task(self._receive_messages())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Close WebSocket connection."""
        await self.close()

    async def connect(self) -> None:
        """Connect to WebSocket server."""
        # Type ignore because `websockets` typing is broken.
        self.websocket = await connect(self.url, extra_headers=self.headers)
        asyncio.create_task(self._receive_messages())

    async def close(self) -> None:
        """Close connection to WebSocket server."""
        if self.websocket and self.websocket.open:
            await self.websocket.close()

    async def _receive_messages(self) -> None:
        if self.websocket is None or not self.websocket.open:
            return
        while True:
            try:
                message = await self.websocket.recv()
                response = json.loads(message)
                request_id = response.get("id")
                self._responses[request_id] = response
                resolver = self._message_resolvers.pop(request_id)
                resolver.set()
            except ConnectionClosedOK:
                break

    async def _send_and_get_json(
        self, request_json: str, request_id: int
    ) -> Union[bytes, str, dict[str, Any]]:
        if self.websocket and self.websocket.open:
            await self.websocket.send(request_json)
        else:
            msg = "WebSocket is not open, call `connect()` first."
            raise RuntimeError(msg)
        event = asyncio.Event()
        self._message_resolvers[request_id] = event
        await event.wait()
        return self._responses.pop(request_id)
