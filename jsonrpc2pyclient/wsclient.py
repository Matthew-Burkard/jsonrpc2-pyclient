"""RPCClient Websocket implementation."""
__all__ = ("AsyncRPCWSClient",)

from types import TracebackType
from typing import Optional, Union

import websockets
from websockets.legacy.client import WebSocketClientProtocol

from jsonrpc2pyclient.rpcclient import AsyncRPCClient


class AsyncRPCWSClient(AsyncRPCClient):
    """A JSON-RPC async Websocket Client."""

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None) -> None:
        """Init async WS client with URL and headers."""
        self._headers = headers
        self.url = url
        self.websocket: Optional[WebSocketClientProtocol] = None
        super(AsyncRPCWSClient, self).__init__()

    async def __aenter__(self) -> "AsyncRPCWSClient":
        """Open WebSocket connection."""
        # Type ignore because `websockets` typing is broken.
        self.websocket = await websockets.connect(  # type: ignore
            self.url, extra_headers=self.headers
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Close WebSocket connection."""
        # Type ignore because `websockets` typing is broken.
        await self.websocket.close()  # type: ignore

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Headers used on websocket connect."""
        return self._headers

    @headers.setter
    def headers(self, headers: dict[str, str]) -> None:
        self._headers = headers

    async def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        if self.websocket is None:
            msg = "WebSocket connection is not established."
            raise ValueError(msg)
        await self.websocket.send(request_json)
        return await self.websocket.recv()
