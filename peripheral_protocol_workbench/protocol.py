from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass(frozen=True)
class Frame:
    message_type: int
    sequence: int
    payload: bytes


def checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def encode_frame(frame: Frame) -> bytes:
    if not 0 <= frame.message_type <= 0xFF:
        raise ValueError("message_type must fit in one byte")
    if not 0 <= frame.sequence <= 0xFFFF:
        raise ValueError("sequence must fit in two bytes")
    if len(frame.payload) > 0xFF:
        raise ValueError("payload too large")

    header = bytes(
        [
            0xAA,
            frame.message_type,
            (frame.sequence >> 8) & 0xFF,
            frame.sequence & 0xFF,
            len(frame.payload),
        ]
    )
    body = header + frame.payload
    return body + bytes([checksum(body)])


def decode_frame(raw: bytes) -> Frame:
    if len(raw) < 6:
        raise ValueError("frame too short")
    if raw[0] != 0xAA:
        raise ValueError("bad start byte")
    payload_length = raw[4]
    expected_length = 6 + payload_length - 0
    if len(raw) != expected_length:
        raise ValueError("frame length mismatch")
    if checksum(raw[:-1]) != raw[-1]:
        raise ValueError("checksum mismatch")
    sequence = (raw[2] << 8) | raw[3]
    payload = raw[5:-1]
    return Frame(message_type=raw[1], sequence=sequence, payload=payload)


class StreamParser:
    """Incremental byte stream parser with resynchronization and recovery."""

    def __init__(self) -> None:
        self.buffer = bytearray()

    def feed(self, data: bytes) -> Iterator[Frame]:
        """Feed bytes into the parser and yield complete decoded frames."""
        self.buffer.extend(data)

        while True:
            # Look for start byte 0xAA
            start_index = self._find_start_byte()
            if start_index < 0:
                # No start byte found, discard all
                self.buffer.clear()
                break
            if start_index > 0:
                # Discard noise before start byte
                del self.buffer[:start_index]

            if len(self.buffer) < 6:
                # Not enough data for minimum frame
                break

            payload_length = self.buffer[4]
            frame_length = 6 + payload_length

            if len(self.buffer) < frame_length:
                # Wait for more data
                break

            candidate = bytes(self.buffer[:frame_length])

            try:
                frame = decode_frame(candidate)
            except ValueError:
                # Bad frame, discard start byte and retry to resync
                del self.buffer[0]
                continue

            # Valid frame found, yield and remove from buffer
            yield frame
            del self.buffer[:frame_length]

    def _find_start_byte(self) -> int:
        try:
            return self.buffer.index(0xAA)
        except ValueError:
            return -1
