from __future__ import annotations

from dataclasses import dataclass

from .protocol import Frame, decode_frame, encode_frame


@dataclass
class ReplayEvent:
    encoded: bytes
    injected_fault: str | None = None


def replay_frames(frames: list[Frame], inject_bad_checksum: bool = False) -> list[ReplayEvent]:
    events: list[ReplayEvent] = []
    for index, frame in enumerate(frames):
        encoded = bytearray(encode_frame(frame))
        fault = None
        if inject_bad_checksum and index == len(frames) - 1:
            encoded[-1] ^= 0xFF
            fault = "checksum_corruption"
        events.append(ReplayEvent(encoded=bytes(encoded), injected_fault=fault))
    return events


def validate_replay(events: list[ReplayEvent]) -> list[str]:
    results: list[str] = []
    for event in events:
        try:
            frame = decode_frame(event.encoded)
            results.append(f"ok:{frame.sequence}")
        except ValueError as exc:
            results.append(f"error:{exc}")
    return results
