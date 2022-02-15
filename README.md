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

### RPCClient Abstract Class

JSON-RPC 2.0 is transport agnostic. This library provides an abstract
class that can be extended to create clients for different transports.

### Implementations

To make client for a transport, extend the `RPCClient` class and
implement the `_send_and_get_json` which takes a request as a str and is
expected to return a JSON-RPC 2.0 response as a str or byte string.
`RPCClient` has a `call` method that uses this internally.

A default HTTP implementation is provided:

```python
class RPCHTTPClient(RPCClient):
    """A JSON-RPC HTTP Client."""

    def __init__(self, url: str, headers: Optional[Headers] = None) -> None:
        self._client = httpx.Client()
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        self._client.headers = headers
        self.url = url
        super(RPCHTTPClient, self).__init__()

    def __del__(self) -> None:
        self._client.close()

    @property
    def headers(self) -> Headers:
        """HTTP headers to be sent with each request."""
        return self._client.headers

    @headers.setter
    def headers(self, headers) -> None:
        self._client.headers = headers

    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:
        return self._client.post(self.url, content=request_json).content
```

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
