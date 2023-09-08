"""IRPCClient abstract class.

This provides functionality that will be shared by the RPCClient and
AsyncRPCClient.
"""
__all__ = ("IRPCClient",)

import json
import logging
from json import JSONDecodeError
from typing import Any, Callable, Optional, Union

from jsonrpcobjects.errors import get_exception_by_code, JSONRPCError, ServerError
from jsonrpcobjects.objects import (
    DataError,
    Error,
    ErrorResponse,
    ParamsRequest,
    Request,
    ResultResponse,
)

log = logging.getLogger(__name__)


class IRPCClient:
    """Abstract class for creating a JSON-RPC client interfaces."""

    def __init__(self) -> None:
        self._pre_call_hooks: list[Callable] = []
        self._ids: dict[int, int] = {}

    @property
    def pre_call_hooks(self) -> list[Callable]:
        """Functions to be called before each method call."""
        return self._pre_call_hooks

    @pre_call_hooks.setter
    def pre_call_hooks(self, pre_call_hooks: list[Callable]) -> None:
        self._pre_call_hooks = pre_call_hooks

    def _get_id(self) -> int:
        new_id = int((max(self._ids.values() or [0]))) + 1
        self._ids[new_id] = new_id
        return new_id

    def _build_request(
        self, method: str, params: Optional[Union[list[Any], dict[str, Any]]]
    ) -> Union[Request, ParamsRequest]:
        if params is not None:
            return ParamsRequest(
                id=self._get_id(),
                method=method,
                params=params,
            )
        return Request(id=self._get_id(), method=method)

    def _get_result_from_response(self, data: Union[bytes, str, dict[str, Any]]) -> Any:
        try:
            # Parse string to JSON.
            json_data = json.loads(data) if not isinstance(data, dict) else data

            # Free ID of this response if `id` field is present.
            if (resp_id := json_data.get("id")) and resp_id in self._ids:
                self._ids.pop(resp_id)

            # Raise error if JSON RPC error response.
            if json_data.get("error"):
                resp = ErrorResponse(**json_data)
                if json_data["error"].get("data"):
                    resp.error = DataError(**json_data["error"])
                else:
                    resp.error = Error(**json_data["error"])
                error = get_exception_by_code(resp.error.code) or ServerError
                raise error(resp.error)

            # Return result if JSON RPC result response.
            if "result" in json_data:
                return ResultResponse(**json_data).result

            # Not valid JSON RPC response if it has no error or result.
            raise JSONRPCError(
                DataError(
                    code=-32000,
                    message="Invalid response from server.",
                    data=json_data,
                )
            )
        except (JSONDecodeError, TypeError, AttributeError) as e:
            log.exception(f"{type(e).__name__}:")
            raise JSONRPCError(
                DataError(
                    code=-32000,
                    message="Invalid response from server.",
                    data=data,
                )
            ) from e
