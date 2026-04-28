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
                # Validate keys
                mt = obj.get("message_type")
                seq = obj.get("sequence")
                payload_hex = obj.get("payload")
                if not isinstance(mt, int) or not isinstance(seq, int) or not isinstance(payload_hex, str):
                    print(f"Skipping invalid frame line: {line}", file=sys.stderr)
                    continue
                payload_bytes = bytes.fromhex(payload_hex)
                yield Frame(message_type=mt, sequence=seq, payload=payload_bytes)
            except Exception as e:
                print(f"Error parsing line: {line} - {e}", file=sys.stderr)


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
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
