from __future__ import annotations

from dataclasses import dataclass


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
