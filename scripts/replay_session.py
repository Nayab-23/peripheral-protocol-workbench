#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Iterator

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(filename: str) -> Iterator[Frame]:
    with open(filename, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Validate keys
                if not all(k in obj for k in ("message_type", "sequence", "payload")):
                    print(f"Skipping line {line_number}: missing required keys", file=sys.stderr)
                    continue
                # Decode payload hex string
                payload_bytes = bytes.fromhex(obj["payload"])
                frame = Frame(
                    message_type=obj["message_type"],
                    sequence=obj["sequence"],
                    payload=payload_bytes,
                )
                yield frame
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Skipping line {line_number}: invalid format ({e})", file=sys.stderr)


def print_frame_summary(frame: Frame, error: str | None = None) -> None:
    summary = (
        f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} "
        f"payload_len={len(frame.payload)}"
    )
    if error:
        summary += f" ERROR: {error}"
    print(summary)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay a captured serial protocol session and print frame summaries."
    )
    parser.add_argument("session_file", help="Path to the JSON lines session file")
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors during replay for testing",
    )

    args = parser.parse_args()

    frames = list(load_frames_from_file(args.session_file))
    if not frames:
        print("No valid frames loaded from session file.", file=sys.stderr)
        return 1

    # Replay frames with optional bad checksum injection
    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    results = validate_replay(replay_iter)

    for result in results:
        # result is a tuple (frame, error_str | None)
        frame, error = result
        print_frame_summary(frame, error)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
