<div align="center">
<!-- Title: -->
  <h1>JSON RPC PyClient</h1>
<!-- Labels: -->
  <!-- First row: -->
  <img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg"
   height="20"
   alt="License: AGPL v3">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"
   height="20"
   alt="Code style: black">
  <img src="https://img.shields.io/pypi/v/jsonrpc2-pyclient.svg"
   height="20"
   alt="PyPI version">
  <a href="https://gitlab.com/mburkard/jsonrpc-pyclient/-/blob/main/CONTRIBUTING.md">
    <img src="https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=00b250"
     height="20"
     alt="Contributions Welcome">
  </a>
  <h3>A library for creating JSON RPC 2.0 clients in Python with async support</h3>
</div>

## Install

```shell
poetry add jsonrpc2-pyclient
```

```shell
pip install jsonrpc2-pyclient
```

## Example

Example of the client decorator implementing rpc methods from reading
method signatures.

```python
import asyncio

from pydantic import BaseModel

from jsonrpc2pyclient.decorator import rpc_client
from jsonrpc2pyclient.httpclient import AsyncRPCHTTPClient

transport = AsyncRPCHTTPClient("http://127.0.0.1:8000/api/v1")


class Vector3(BaseModel):
    x: float = 1.0
    y: float = 1.0
    z: float = 1.0


@rpc_client(transport=transport)
class TestClient:
    async def add(self, a: int, b: int) -> int: ...
    async def get_distance(self, a: Vector3, b: Vector3) -> Vector3: ...


async def main() -> None:
    client = TestClient()
    assert await client.add(3, 4) == 7
    assert await client.get_distance(Vector3(), Vector3()) == Vector3(x=0, y=0, z=0)


if __name__ == "__main__":
    asyncio.run(main())
```

### RPCClient Abstract Class

JSON-RPC 2.0 is transport agnostic. This library provides an abstract
class that can be extended to create clients for different transports.

### Transports

To make client for a transport, extend the `RPCClient` class and
implement the `_send_and_get_json` which takes a request as a str and is
expected to return a JSON-RPC 2.0 response as a str or byte string.
`RPCClient` has a `call` method that uses this internally.

A default HTTP and Websocket implementation is provided.

### Usage

The `RPCClient` will handle forming requests and parsing responses.
To call a JSON-RPC 2.0 method with an implementation of `RPCClient`,
call the `call` method, passing it the name of the method to call and
the params.

If the response is JSON-RPC 2.0 result object, only the result will be
returned, none of the wrapper.

If the response is JSON-RPC 2.0 error response, and exception will be
thrown for the error.

```python
from jsonrpc2pyclient.httpclient import RPCHTTPClient
from jsonrpcobjects.errors import JSONRPCError

client = RPCHTTPClient("http://localhost:5000/api/v1/")
try:
    res = client.call("divide", [0, 0])
    print(f"JSON-RPC Result: {res}")
except JSONRPCError as e:
    print(f"JSON-RPC Error: {e}")
```

## Client Decorator

The `rpc_client` decorator can be used to quickly put together a client
with typed methods. When a class is decorated, each method defined in
that class will make RPC requests using the provided transport and parse
the result. The name of the method will be used in the RPC request.

The method body must end with `...` for the decorator to implement it.

```python
transport = RPCHTTPClient("http://127.0.0.1:8000/api/v1")

@rpc_client(transport=transport)
class TestClient:
    def add(self, a: int, b: int) -> int: ...


client = TestClient()
assert client.add(3, 4) == 7
```
