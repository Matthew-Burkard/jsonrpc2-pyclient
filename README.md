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
pip install jsonrpc2-pyclient
```

## Usage

### RPC Client Abstract Class

The RPCClient abstract class provides methods to ease the development of
an RPC Client for any transport method. It parses JSON-RPC 2.0 requests
and responses.

To use, an implementation only needs to override the
`_send_and_get_json` method. This method is used internally.
JSONRPCClient will pass it a request as a JSON string and expect a
response as JSON string.

A simple implementation:

```python
class RPCHTTPClient(RPCClient):

    def __init__(self, url: str) -> None:
        self.url = url
        super(RPCHTTPClient, self).__init__()

    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return requests.post(url=self.url, data=request_json).content
```

### Default HTTP Client

This module provides a default HTTP implementation of the RPCClient.

#### Example HTTP Client Usage

If a JSON RPC server defines the methods "add", "subtract", and
"divide", expecting the following requests:

```json
{
  "id": 1,
  "method": "add",
  "params": [2, 3],
  "jsonrpc": "2.0"
}

{
  "id": 2,
  "method": "subtract",
  "params": [2, 3],
  "jsonrpc": "2.0"
}

{
  "id": 3,
  "method": "divide",
  "params": [3, 2],
  "jsonrpc": "2.0"
}
```

Defining and using the corresponding client would look like this:

```python
class MathClient(RPCHTTPClient):
    def add(self, a: int, b: int) -> int:
        return self.call('add', [a, b])

    def subtract(self, a: int, b: int) -> int:
        return self.call('subtract', [a, b])

    def divide(self, a: int, b: int) -> float:
        return self.call('divide', [a, b])


client = MathClient('http://localhost:5000/api/v1')
client.add(2, 3)  # 5
client.subtract(2, 3)  # -1
client.divide(2, 2)  # 1
```

Notice, just the result field of the JSON-RPC response object is
returned by `call`, not the whole object.

## Errors

If the server responds with an error, an RpcError is thrown.

There is an RpcError for each standard JSON RPC 2.0 error, each of them
extends RpcError.

```python
client = MathClient('http://localhost:5000/api/v1')

try:
    client.add('two', 'three')
except InvalidParams as e:
    log.exception(f'{type(e).__name__}:')

try:
    client.divide(0, 0)
except ServerError as e:
    log.exception(f'{type(e).__name__}:')
```

### Async Support (v1.1+)

Async alternatives to the RPCClient ABC and RPCHTTPClient are available.

```python
class AsyncMathClient(AsyncRPCHTTPClient):
    async def add(self, a: int, b: int) -> int:
        return await self.call('add', [a, b])

    async def subtract(self, a: int, b: int) -> int:
        return await self.call('subtract', [a, b])

    async def divide(self, a: int, b: int) -> float:
        return await self.call('divide', [a, b])
```
