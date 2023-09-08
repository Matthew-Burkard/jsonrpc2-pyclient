"""RPCClient HTTP implementation."""
__all__ = ("AsyncRPCHTTPClient", "RPCHTTPClient")

from typing import Optional, Union

import httpx
from httpx import Headers

from jsonrpc2pyclient.rpcclient import AsyncRPCClient, RPCClient


class AsyncRPCHTTPClient(AsyncRPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[Headers] = None) -> None:
        """Init async HTTP client with URL and headers."""
        headers = headers or Headers()
        headers["Content-Type"] = "application/json"
        self._headers = headers
        self.url = url
        super(AsyncRPCHTTPClient, self).__init__()

    @property
    def headers(self) -> Headers:
        """HTTP headers to be sent with each request."""
        return self._headers

    @headers.setter
    def headers(self, headers: Union[Headers | dict[str, str]]) -> None:
        self._headers = Headers(headers)

    async def _send_and_get_json(
        self,
        request_json: str,
        # `noqa` since ARG002 wrongfully applies to abc methods.
        request_id: int,  # noqa: ARG002
    ) -> Union[bytes, str]:
        async with httpx.AsyncClient() as client:
            client.headers = Headers({**client.headers, **self.headers})
            return (await client.post(self.url, content=request_json)).content


class RPCHTTPClient(RPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[Headers] = None) -> None:
        """Init HTTP client with URL and headers."""
        self._client = httpx.Client()
        headers = headers or Headers()
        headers["Content-Type"] = "application/json"
        self._client.headers = headers
        self.url = url
        super(RPCHTTPClient, self).__init__()

    @property
    def headers(self) -> Headers:
        """HTTP headers to be sent with each request."""
        return self._client.headers

    @headers.setter
    def headers(self, headers: Union[Headers | dict[str, str]]) -> None:
        self._client.headers = Headers(headers)

    def _send_and_get_json(
        self,
        request_json: str,
        # `noqa` since ARG002 wrongfully applies to abc methods.
        request_id: int,  # noqa: ARG002
    ) -> Union[bytes, str]:
        return self._client.post(self.url, content=request_json).content
