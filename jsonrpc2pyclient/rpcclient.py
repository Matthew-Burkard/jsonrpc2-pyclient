"""This module provides the RPCClient abstract class."""
import abc
import inspect
from typing import Any, Optional, Union

from jsonrpc2pyclient._irpcclient import IRPCClient

__all__ = ("AsyncRPCClient", "RPCClient")


class AsyncRPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating async JSON-RPC clients."""

    @abc.abstractmethod
    async def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        ...

    async def call(
        self, method: str, params: Optional[Union[list, dict[str, Any]]] = None
    ) -> Any:
        """Call a method with the provided params."""
        for hook in self.pre_call_hooks:
            await hook() if inspect.iscoroutinefunction(hook) else hook()
        request = self._build_request(method, params)
        data = await self._send_and_get_json(request.json(by_alias=True))
        return self._get_result_from_response(data)


class RPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating a JSON-RPC clients."""

    @abc.abstractmethod
    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        ...

    def call(
        self, method: str, params: Optional[Union[list, dict[str, Any]]] = None
    ) -> Any:
        """Call a method with the provided params."""
        request = self._build_request(method, params)
        for hook in self.pre_call_hooks:
            hook()
        return self._get_result_from_response(
            self._send_and_get_json(request.json(by_alias=True))
        )
