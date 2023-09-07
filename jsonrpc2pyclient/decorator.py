"""BaseClient for quickly creating typed RPC clients."""
import functools
import inspect
import re
from typing import Any, Callable, ForwardRef, Optional, TypeVar, Union

from pydantic import create_model

# noinspection PyProtectedMember
from pydantic.v1.typing import evaluate_forwardref

from jsonrpc2pyclient.rpcclient import AsyncRPCClient, RPCClient

BaseClient = TypeVar("BaseClient")
ClientType = Union[AsyncRPCClient, RPCClient]


def rpc_client(
    transport: ClientType, method_prefix: Optional[str] = None
) -> Callable[[BaseClient], BaseClient]:
    """Add RPC implementations for the decorated classes methods."""

    def _wrapper(cls: BaseClient) -> BaseClient:
        for attr in dir(cls):
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                source = inspect.getsource(getattr(cls, attr))
                if re.match(r"^ *(async )?def.*?\.\.\.\n$", source, re.S):
                    setattr(
                        cls,
                        attr,
                        rpc_method(transport, method_prefix)(getattr(cls, attr)),
                    )
        return cls

    return _wrapper


def rpc_method(
    transport: ClientType, prefix: Optional[str], *, by_position: bool = True
) -> Callable:
    """Use types of decorated method to call RPC method on call."""

    def _decorator(function: Callable) -> Callable:
        name = (prefix or "") + function.__name__
        signature = inspect.signature(function)
        param_model = create_model(  # type: ignore
            f"{name}Params",
            **{
                k: (
                    resolved_annotation(v.annotation, function),
                    v.default if v.default is not inspect.Signature.empty else ...,
                )
                for k, v in signature.parameters.items()
                if k != "self"
            },
        )
        result_model = create_model(
            f"{name}Result",
            result=(resolved_annotation(signature.return_annotation, function), ...),
        )

        @functools.wraps(function)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            params_dict: dict[str, Any] = kwargs
            for i, field_name in enumerate(param_model.model_fields):
                # Offset by 1 to skip `self` arg.
                if i < len(args) - 1:
                    params_dict[field_name] = args[i + 1]
            params = list(params_dict.values()) if by_position else params_dict
            # Type ignore because mypy is wrong.
            resp = await transport.call(name, params)  # type: ignore
            # Cast to proper return type.
            # Type ignore because mypy can't understand `create_model`.
            return result_model(result=resp).result  # type: ignore

        return _wrapper

    return _decorator


def resolved_annotation(annotation: Any, function: Callable) -> Any:
    """Get annotation resolved."""
    if annotation == inspect.Signature.empty:
        return Any
    globalns = getattr(function, "__globals__", {})
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return type(None) if annotation is None else annotation
