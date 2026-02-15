"""Transport interface contract for deterministic protocol exchanges."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class Transport(ABC):
    """Minimal pluggable transport interface.

    Contract:
    - Implementations may differ in delivery timing.
    - Protocol accept/refuse decisions must remain content-deterministic.
    """

    @property
    @abstractmethod
    def transport_id(self) -> str:
        """Stable transport identifier."""

    @abstractmethod
    def connect(self, endpoint: str) -> Dict[str, object]:
        """Connect as client to an endpoint."""

    @abstractmethod
    def accept(self) -> Dict[str, object]:
        """Accept next pending server-side connection."""

    @abstractmethod
    def send(self, message_bytes: bytes) -> Dict[str, object]:
        """Send message bytes over current connection."""

    @abstractmethod
    def recv(self) -> Dict[str, object]:
        """Receive message bytes from current connection."""

    @abstractmethod
    def close(self) -> Dict[str, object]:
        """Close transport/connection resources."""
