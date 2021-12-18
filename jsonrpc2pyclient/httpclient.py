"""This module provides the RPCClient HTTP implementation."""
import asyncio
from typing import Optional, Union

import httpx
from httpx import Headers

from jsonrpc2pyclient.rpcclient import AsyncRPCClient, RPCClient

__all__ = ("AsyncRPCHTTPClient", "RPCHTTPClient",)


class AsyncRPCHTTPClient(AsyncRPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[dict] = None) -> None:
        self._client = httpx.AsyncClient()
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        self._client.headers = headers
        self.url = url
        super(AsyncRPCHTTPClient, self).__init__()

    def __del__(self) -> None:
        asyncio.ensure_future(self._client.aclose())

    @property
    def headers(self) -> Headers:
        """HTTP headers to be sent with each request."""
        return self._client.headers

    @headers.setter
    def headers(self, headers) -> None:
        self._client.headers = headers

    async def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return (await self._client.post(self.url, content=request_json)).content


class RPCHTTPClient(RPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[dict] = None) -> None:
        self._client = httpx.Client()
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        self._client.headers = headers
        self.url = url
        super(RPCHTTPClient, self).__init__()

    def __del__(self) -> None:
        self._client.close()

    @property
    def headers(self) -> Headers:
        """HTTP headers to be sent with each request."""
        return self._client.headers

    @headers.setter
    def headers(self, headers) -> None:
        self._client.headers = headers

    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return self._client.post(self.url, content=request_json).content
