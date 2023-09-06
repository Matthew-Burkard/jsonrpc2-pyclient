"""RPCClient abstract classes for sync and async RPC clients."""
import abc
import inspect
from typing import Any, Optional, Union

from jsonrpc2pyclient._irpcclient import IRPCClient

__all__ = ("AsyncRPCClient", "RPCClient")


class AsyncRPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating async JSON-RPC clients."""

    @abc.abstractmethod
    async def _send_and_get_json(
        self, request_json: str, request_id: Optional[int] = None
    ) -> Union[bytes, str, dict[str, Any]]:
        ...

    async def call(
        self, method: str, params: Optional[Union[list[Any], dict[str, Any]]] = None
    ) -> Any:
        """Call a method with the provided params."""
        for hook in self.pre_call_hooks:
            await hook() if inspect.iscoroutinefunction(hook) else hook()
        request = self._build_request(method, params)
        data = await self._send_and_get_json(
            request.model_dump_json(by_alias=True), request.id
        )
        return self._get_result_from_response(data)


class RPCClient(abc.ABC, IRPCClient):
    """Abstract class for creating a JSON-RPC clients."""

    @abc.abstractmethod
    def _send_and_get_json(
        self, request_json: str, request_id: Optional[int] = None
    ) -> Union[bytes, str, dict[str, Any]]:
        ...

    def call(
        self, method: str, params: Optional[Union[list[Any], dict[str, Any]]] = None
    ) -> Any:
        """Call a method with the provided params."""
        request = self._build_request(method, params)
        for hook in self.pre_call_hooks:
            hook()
        return self._get_result_from_response(
            self._send_and_get_json(request.model_dump_json(by_alias=True))
        )
