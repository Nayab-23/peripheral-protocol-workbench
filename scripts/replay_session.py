#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Iterator

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(filename: str) -> Iterator[Frame]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Convert payload hex string to bytes
                payload_bytes = bytes.fromhex(obj["payload"])
                frame = Frame(
                    message_type=obj["message_type"],
                    sequence=obj["sequence"],
                    payload=payload_bytes,
                )
                yield frame
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Skipping invalid line: {line} ({e})", file=sys.stderr)


def print_frame_summary(frame: Frame) -> None:
    # Print a concise summary of the frame
    payload_preview = frame.payload.decode(errors='replace')
    if len(payload_preview) > 40:
        payload_preview = payload_preview[:37] + "..."
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload='{payload_preview}' checksum_valid={frame.checksum_valid}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the JSON lines session file")
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors into replayed frames for testing",
    )

    args = parser.parse_args()

    frames = list(load_frames_from_file(args.session_file))
    if not frames:
        print(f"No valid frames loaded from {args.session_file}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print_frame_summary(result.frame)
        if result.error:
            print(f"  Error: {result.error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
