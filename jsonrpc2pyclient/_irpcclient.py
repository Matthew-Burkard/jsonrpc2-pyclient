"""This module provides the IRPCClient abstract class.

This provides functionality that will be shared by the RPCClient and
AsyncRPCClient.
"""
import json
import logging
from json import JSONDecodeError
from typing import Union

from jsonrpcobjects.errors import get_exception_by_code, JSONRPCError, ServerError
from jsonrpcobjects.jsontypes import JSONStructured
from jsonrpcobjects.objects import (
    ErrorObject,
    ErrorObjectData,
    ErrorResponseObject,
    RequestObject,
    RequestObjectParams,
    ResultResponseObject,
)

__all__ = ("IRPCClient",)
log = logging.getLogger(__name__)


class IRPCClient:
    """Abstract class for creating a JSON-RPC client interfaces."""

    def __init__(self) -> None:
        self._ids = {}

    def _get_id(self) -> int:
        new_id = (max(self._ids.values() or [0])) + 1
        self._ids[new_id] = new_id
        return new_id

    def _build_request(
        self, method: str, params: JSONStructured
    ) -> Union[RequestObject, RequestObjectParams]:
        if params is not None:
            return RequestObjectParams(
                id=self._get_id(),
                method=method,
                params=params,
            )
        return RequestObject(id=self._get_id(), method=method)

    def _get_result_from_response(self, data: Union[bytes, str]):
        try:
            json_data = json.loads(data)
            if resp_id := json_data.get("id"):
                try:
                    self._ids.pop(resp_id)
                except KeyError:
                    pass
            if json_data.get("error"):
                resp = ErrorResponseObject(**json_data)
                if json_data["error"].get("data"):
                    resp.error = ErrorObjectData(**json_data["error"])
                else:
                    resp.error = ErrorObject(**json_data["error"])
                error = get_exception_by_code(resp.error.code) or ServerError
                raise error(resp.error)
            if "result" in json_data.keys():
                return ResultResponseObject(**json_data).result
            raise JSONRPCError(
                ErrorObjectData(
                    code=-32000,
                    message="Invalid response from server.",
                    data=json_data,
                )
            )
        except (JSONDecodeError, TypeError, AttributeError) as e:
            log.exception(f"{type(e).__name__}:")
            raise JSONRPCError(
                ErrorObjectData(
                    code=-32000,
                    message="Invalid response from server.",
                    data=data,
                )
            )
