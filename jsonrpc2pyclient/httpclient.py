"""This module provides the RPCClient HTTP implementation."""
from typing import Optional, Union

import httpx

from jsonrpc2pyclient.rpcclient import RPCClient


class RPCHTTPClient(RPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[dict] = None) -> None:
        self.client = httpx.Client()
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        self.client.headers = headers
        self.url = url
        super(RPCHTTPClient, self).__init__()

    def __del__(self) -> None:
        self.client.close()

    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return self.client.post(self.url, content=request_json).content
