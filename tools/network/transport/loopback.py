"""Deterministic in-process loopback transport."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List

from .interface import Transport


def _sort_unique_strings(values: List[str]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _conn_id(endpoint: str, client_peer_id: str, serial: int) -> str:
    token = "{}|{}|{}".format(str(endpoint), str(client_peer_id), int(serial))
    return "loop.conn.{}".format(hashlib.sha256(token.encode("utf-8")).hexdigest()[:16])


def _result_complete(**extra) -> Dict[str, object]:
    out: Dict[str, object] = {"result": "complete"}
    out.update(extra)
    return out


def _result_refused(reason_code: str, message: str) -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
        },
    }


@dataclass
class _LoopbackConnection:
    connection_id: str
    endpoint: str
    client_peer_id: str
    server_peer_id: str
    client_to_server: List[bytes] = field(default_factory=list)
    server_to_client: List[bytes] = field(default_factory=list)
    client_closed: bool = False
    server_closed: bool = False


@dataclass
class _LoopbackListener:
    endpoint: str
    server_peer_id: str
    pending_connection_ids: List[str] = field(default_factory=list)
    next_serial: int = 1


_LISTENERS: Dict[str, _LoopbackListener] = {}
_CONNECTIONS: Dict[str, _LoopbackConnection] = {}


def reset_loopback_state() -> None:
    """Test helper: clear deterministic in-memory loopback state."""
    _LISTENERS.clear()
    _CONNECTIONS.clear()


class LoopbackTransport(Transport):
    """Deterministic loopback transport with explicit listen/connect/accept semantics."""

    def __init__(self, peer_id: str, role: str = "client", endpoint: str = "") -> None:
        self.peer_id = str(peer_id).strip()
        self._role = str(role).strip() or "client"
        self._endpoint = str(endpoint).strip()
        self._connection_id = ""
        self._remote_peer_id = ""

    @property
    def transport_id(self) -> str:
        return "transport.loopback"

    @property
    def role(self) -> str:
        return str(self._role)

    @property
    def endpoint(self) -> str:
        return str(self._endpoint)

    @property
    def connection_id(self) -> str:
        return str(self._connection_id)

    @property
    def remote_peer_id(self) -> str:
        return str(self._remote_peer_id)

    @classmethod
    def listen(cls, endpoint: str, server_peer_id: str) -> "LoopbackTransport":
        endpoint_token = str(endpoint).strip()
        if not endpoint_token:
            raise ValueError("loopback listen endpoint must be non-empty")
        server_token = str(server_peer_id).strip()
        if not server_token:
            raise ValueError("loopback server_peer_id must be non-empty")
        listener = _LISTENERS.get(endpoint_token)
        if listener is None:
            _LISTENERS[endpoint_token] = _LoopbackListener(
                endpoint=endpoint_token,
                server_peer_id=server_token,
            )
        else:
            listener.server_peer_id = server_token
            listener.pending_connection_ids = _sort_unique_strings(listener.pending_connection_ids)
        return cls(peer_id=server_token, role="server_listener", endpoint=endpoint_token)

    def connect(self, endpoint: str) -> Dict[str, object]:
        if self._role not in ("client", "client_connected"):
            return _result_refused("refusal.net.transport_role_invalid", "connect requires client role")
        endpoint_token = str(endpoint).strip()
        if not endpoint_token:
            return _result_refused("refusal.net.transport_endpoint_invalid", "endpoint must be non-empty")
        listener = _LISTENERS.get(endpoint_token)
        if listener is None:
            return _result_refused("refusal.net.transport_endpoint_missing", "loopback endpoint has no listener")

        serial = int(listener.next_serial)
        listener.next_serial = serial + 1
        connection_id = _conn_id(endpoint=endpoint_token, client_peer_id=self.peer_id, serial=serial)
        connection = _LoopbackConnection(
            connection_id=connection_id,
            endpoint=endpoint_token,
            client_peer_id=self.peer_id,
            server_peer_id=listener.server_peer_id,
        )
        _CONNECTIONS[connection_id] = connection
        listener.pending_connection_ids.append(connection_id)
        listener.pending_connection_ids = _sort_unique_strings(listener.pending_connection_ids)

        self._endpoint = endpoint_token
        self._connection_id = connection_id
        self._remote_peer_id = str(listener.server_peer_id)
        self._role = "client_connected"
        return _result_complete(
            transport_id=self.transport_id,
            endpoint=self._endpoint,
            connection_id=self._connection_id,
            peer_id=self.peer_id,
            remote_peer_id=self._remote_peer_id,
        )

    def accept(self) -> Dict[str, object]:
        if self._role != "server_listener":
            return _result_refused("refusal.net.transport_role_invalid", "accept requires server listener role")
        if not self._endpoint:
            return _result_refused("refusal.net.transport_endpoint_invalid", "listener endpoint is missing")
        listener = _LISTENERS.get(self._endpoint)
        if listener is None:
            return _result_refused("refusal.net.transport_endpoint_missing", "loopback listener endpoint is missing")
        pending = _sort_unique_strings(listener.pending_connection_ids)
        listener.pending_connection_ids = list(pending)
        if not pending:
            return {"result": "empty", "transport_id": self.transport_id, "endpoint": self._endpoint}
        connection_id = str(pending[0])
        listener.pending_connection_ids = [token for token in pending[1:]]
        connection = _CONNECTIONS.get(connection_id)
        if connection is None:
            return _result_refused("refusal.net.transport_connection_missing", "pending connection missing")
        self._connection_id = connection_id
        self._remote_peer_id = str(connection.client_peer_id)
        self._role = "server_connected"
        return _result_complete(
            transport_id=self.transport_id,
            endpoint=self._endpoint,
            connection_id=self._connection_id,
            peer_id=self.peer_id,
            remote_peer_id=self._remote_peer_id,
        )

    def send(self, message_bytes: bytes) -> Dict[str, object]:
        if self._role not in ("client_connected", "server_connected"):
            return _result_refused("refusal.net.transport_not_connected", "send requires an active connection")
        connection = _CONNECTIONS.get(self._connection_id)
        if connection is None:
            return _result_refused("refusal.net.transport_connection_missing", "active connection is missing")
        payload = bytes(message_bytes or b"")
        if self._role == "client_connected":
            if connection.client_closed:
                return _result_refused("refusal.net.transport_connection_closed", "client connection is closed")
            connection.client_to_server.append(payload)
            queue_size = len(connection.client_to_server)
        else:
            if connection.server_closed:
                return _result_refused("refusal.net.transport_connection_closed", "server connection is closed")
            connection.server_to_client.append(payload)
            queue_size = len(connection.server_to_client)
        return _result_complete(connection_id=self._connection_id, bytes=len(payload), queue_size=queue_size)

    def recv(self) -> Dict[str, object]:
        if self._role not in ("client_connected", "server_connected"):
            return _result_refused("refusal.net.transport_not_connected", "recv requires an active connection")
        connection = _CONNECTIONS.get(self._connection_id)
        if connection is None:
            return _result_refused("refusal.net.transport_connection_missing", "active connection is missing")

        if self._role == "client_connected":
            queue = connection.server_to_client
        else:
            queue = connection.client_to_server
        if not queue:
            return {"result": "empty", "connection_id": self._connection_id, "message_bytes": b""}
        payload = queue.pop(0)
        return _result_complete(connection_id=self._connection_id, message_bytes=bytes(payload))

    def close(self) -> Dict[str, object]:
        if self._role == "server_listener":
            if self._endpoint in _LISTENERS:
                del _LISTENERS[self._endpoint]
            self._role = "closed"
            self._endpoint = ""
            self._connection_id = ""
            self._remote_peer_id = ""
            return _result_complete(transport_id=self.transport_id, closed=True)

        if self._role in ("client_connected", "server_connected"):
            connection = _CONNECTIONS.get(self._connection_id)
            if connection is not None:
                if self._role == "client_connected":
                    connection.client_closed = True
                else:
                    connection.server_closed = True
                if connection.client_closed and connection.server_closed:
                    del _CONNECTIONS[self._connection_id]
            self._role = "closed"
            self._connection_id = ""
            self._remote_peer_id = ""
            return _result_complete(transport_id=self.transport_id, closed=True)

        self._role = "closed"
        self._connection_id = ""
        self._remote_peer_id = ""
        return _result_complete(transport_id=self.transport_id, closed=True)
