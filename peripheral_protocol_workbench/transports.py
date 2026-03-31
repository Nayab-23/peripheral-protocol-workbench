from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class TransportError(RuntimeError):
    pass


class Transport:
    def send(self, payload: bytes) -> None:
        raise NotImplementedError

    def receive(self) -> bytes:
        raise NotImplementedError


@dataclass
class LoopbackTransport(Transport):
    queue: deque[bytes] = field(default_factory=deque)

    def send(self, payload: bytes) -> None:
        self.queue.append(payload)

    def receive(self) -> bytes:
        if not self.queue:
            raise TransportError("no payload available")
        return self.queue.popleft()
