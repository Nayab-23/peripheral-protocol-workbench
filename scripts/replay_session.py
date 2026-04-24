#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Iterator

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(path: str) -> Iterator[Frame]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            # Convert payload hex string to bytes
            payload_bytes = bytes.fromhex(obj["payload"])
            yield Frame(
                message_type=obj["message_type"],
                sequence=obj["sequence"],
                payload=payload_bytes,
            )


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

    try:
        frames = list(load_frames_from_file(args.session_file))
    except Exception as e:
        print(f"Error reading session file: {e}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
