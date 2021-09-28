import abc
import json
import logging
from json import JSONDecodeError
from typing import Any, Optional, Type, Union

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

__all__ = ("RPCClient",)
log = logging.getLogger(__name__)


class RPCClient(abc.ABC):
    def __init__(self) -> None:
        self._ids = {}

    @property
    def server_errors(self) -> dict[int, Type]:
        return {}

    def _get_id(self) -> int:
        new_id = (max(self._ids.values() or [0])) + 1
        self._ids[new_id] = new_id
        return new_id

    @abc.abstractmethod
    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        ...

    def _call(self, method: str, params: Optional[JSONStructured] = None) -> Any:
        # Build request object.
        if params is not None:
            request = RequestObjectParams(
                id=self._get_id(),
                method=method,
                params=params,
            )
        else:
            request = RequestObject(id=self._get_id(), method=method)
        # Send request JSON and get JSON response.
        data = self._send_and_get_json(request.json())
        # Return result or raise error.
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
