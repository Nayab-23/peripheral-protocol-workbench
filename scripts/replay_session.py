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
                mt = obj["message_type"]
                seq = obj["sequence"]
                payload_hex = obj["payload"]
                payload_bytes = bytes.fromhex(payload_hex)
                yield Frame(message_type=mt, sequence=seq, payload=payload_bytes)
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"Error parsing line {line_number}: {e}", file=sys.stderr)
                sys.exit(1)


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

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
