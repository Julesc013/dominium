"""Optional TCP transport stub for MP-2 contract phase."""

from __future__ import annotations

from typing import Dict

from .interface import Transport


class TcpTransportStub(Transport):
    """Placeholder transport with explicit deterministic refusal."""

    @property
    def transport_id(self) -> str:
        return "transport.tcp"

    def connect(self, endpoint: str) -> Dict[str, object]:
        return {
            "result": "refused",
            "refusal": {
                "reason_code": "refusal.not_implemented.net_transport",
                "message": "transport.tcp is not implemented in MP-2",
            },
        }

    def accept(self) -> Dict[str, object]:
        return self.connect("")

    def send(self, message_bytes: bytes) -> Dict[str, object]:
        del message_bytes
        return self.connect("")

    def recv(self) -> Dict[str, object]:
        return self.connect("")

    def close(self) -> Dict[str, object]:
        return {"result": "complete", "transport_id": self.transport_id, "closed": True}
