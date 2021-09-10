from typing import Any, Optional

from jsonrpcobjects.objects import RequestType
from requests import Session

from jsonrpc2pyclient.rpcclient import RPCClient


class RPCHTTPClient(RPCClient):
    def __init__(
            self, session: Session,
            url: str,
            headers: Optional[dict] = None
    ) -> None:
        self.session = session
        self.url = url
        self.headers = headers or {'contentType': 'application/json'}

    def _send_request(self, request: RequestType) -> Any:
        resp = self.session.post(
            url=self.url,
            data=request.json(by_alias=True),
            headers=self.headers
        )
        return self._parse_json(resp.content)
