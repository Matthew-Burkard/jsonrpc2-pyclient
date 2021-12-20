"""This module provides the RPCClient abstract class."""
import abc
import inspect
from typing import Any, Optional, Union

from jsonrpcobjects.jsontypes import JSONStructured

from jsonrpc2pyclient._irpcclient import IRPCClient

__all__ = ("AsyncRPCClient", "RPCClient")


class AsyncRPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating async JSON-RPC clients."""

    @abc.abstractmethod
    async def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        ...

    async def call(self, method: str, params: Optional[JSONStructured] = None) -> Any:
        """Call a method with the provided params."""
        [
            await f() if inspect.iscoroutinefunction(f) else f()
            for f in self.pre_call_hooks
        ]
        request = self._build_request(method, params)
        data = await self._send_and_get_json(request.json(by_alias=True))
        return self._get_result_from_response(data)


class RPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating a JSON-RPC clients."""

    @abc.abstractmethod
    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        ...

    def call(self, method: str, params: Optional[JSONStructured] = None) -> Any:
        """Call a method with the provided params."""
        request = self._build_request(method, params)
        [f() for f in self.pre_call_hooks]
        return self._get_result_from_response(
            self._send_and_get_json(request.json(by_alias=True))
        )
