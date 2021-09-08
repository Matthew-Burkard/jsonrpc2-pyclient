import abc
import json
import logging
import sys
from json import JSONDecodeError
from random import randint
from typing import Any, Union, Type

from jsonrpcobjects.errors import (
    get_exception_by_code,
    ServerError,
    JSONRPCError,
)
from jsonrpcobjects.objects import (
    RequestType,
    ResultResponseObject,
    ResponseType,
    ErrorObject,
    ErrorObjectData,
    ErrorResponseObject,
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
    def _send_request(self, request: RequestType) -> Any: ...

    def _parse_json(self, data: Union[bytes, str]) -> Any:
        resp = _parse_response(data)
        if isinstance(resp, ResultResponseObject):
            return resp.result
        if -32000 >= resp.error.code > -32100:
            error = self.server_errors.get(resp.error.code) or ServerError
            raise error(resp.error)
        raise get_exception_by_code(resp.error.code)


def _parse_response(data: Union[bytes, str]) -> ResponseType:
    try:
        resp = json.loads(data)
        if resp.get('error'):
            error_resp = ErrorResponseObject(**resp)
            if resp['error'].get('data'):
                error_resp.error = ErrorObjectData(**resp['error'])
            else:
                error_resp.error = ErrorObject(**resp['error'])
            return error_resp
        if 'result' in resp.keys():
            return ResultResponseObject(**resp)
        raise JSONRPCError(
            ErrorObject(code=-32000, message='Unable to parse response.')
        )
    except (JSONDecodeError, TypeError, AttributeError) as e:
        log.exception(f'{type(e).__name__}:')
        raise JSONRPCError(
            ErrorObject(code=-32000, message='Unable to parse response.')
        )
