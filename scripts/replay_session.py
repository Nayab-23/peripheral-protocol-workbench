#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Iterator

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(file_path: str) -> Iterator[Frame]:
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Convert hex string payload to bytes
                payload_bytes = bytes.fromhex(obj["payload"])
                frame = Frame(
                    message_type=obj["message_type"],
                    sequence=obj["sequence"],
                    payload=payload_bytes,
                )
                yield frame
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"Skipping invalid line: {line}\nError: {e}", file=sys.stderr)


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
    results = validate_replay(replay_iter)

    for result in results:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
