import abc
import json
import logging
import sys
from json import JSONDecodeError
from random import randint
from typing import Any, Union, Type, Optional

from jsonrpcobjects.errors import (
    get_exception_by_code,
    ServerError,
    JSONRPCError,
)
from jsonrpcobjects.jsontypes import JSONStructured
from jsonrpcobjects.objects import (
    ResultResponseObject,
    ErrorObject,
    ErrorObjectData,
    ErrorResponseObject,
    RequestObject,
    RequestObjectParams,
)

__all__ = ('RPCClient',)
log = logging.getLogger(__name__)


class RPCClient(abc.ABC):

    @property
    def server_errors(self) -> dict[int, Type]:
        return {}

    @staticmethod
    def _gen_id() -> Union[str, int]:
        return randint(1, sys.maxsize)

    @abc.abstractmethod
    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]: ...

    def _call(
            self,
            method: str,
            params: Optional[JSONStructured] = None
    ) -> Any:
        # Build request object.
        if params is not None:
            request = RequestObjectParams(
                id=self._gen_id(),
                method=method,
                params=params,
            )
        else:
            request = RequestObject(id=self._gen_id(), method=method)
        # Send request JSON and get JSON response.
        data = self._send_and_get_json(request.json())
        # Return result or raise error.
        try:
            resp = json.loads(data)
            if resp.get('error'):
                error_resp = ErrorResponseObject(**resp)
                if resp['error'].get('data'):
                    error_resp.error = ErrorObjectData(**resp['error'])
                else:
                    error_resp.error = ErrorObject(**resp['error'])
                error = get_exception_by_code(resp.error.code) or ServerError
                raise error(error_resp.error)
            if resp.get('result'):
                return ResultResponseObject(**resp).result
            raise JSONRPCError(
                ErrorObjectData(
                    code=-32000,
                    message='Invalid response from server.',
                    data=resp,
                )
            )
        except (JSONDecodeError, TypeError, AttributeError) as e:
            log.exception(f'{type(e).__name__}:')
            raise JSONRPCError(
                ErrorObjectData(
                    code=-32000,
                    message='Invalid response from server.',
                    data=data,
                )
            )
