#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Iterator

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(file_path: str) -> Iterator[Frame]:
    with open(file_path, "r", encoding="utf-8") as f:
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
                # Decode payload hex string to bytes
                payload_bytes = bytes.fromhex(obj["payload"])
                frame = Frame(
                    message_type=obj["message_type"],
                    sequence=obj["sequence"],
                    payload=payload_bytes,
                )
                yield frame
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Skipping line {line_number}: invalid format ({e})", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the JSON lines session file")
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors into replayed frames for testing",
    )

    args = parser.parse_args()

    try:
        frames = list(load_frames_from_file(args.session_file))
    except FileNotFoundError:
        print(f"Error: file not found: {args.session_file}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
