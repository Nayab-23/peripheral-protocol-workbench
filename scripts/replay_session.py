#!/usr/bin/env python3
import argparse
import json
import sys
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay a captured protocol session and print frame summaries."
    )
    parser.add_argument(
        "session_file",
        type=argparse.FileType("r"),
        help="Path to the JSON lines session file",
    )
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors during replay for testing",
    )
    return parser.parse_args()

def load_frames(file) -> list[Frame]:
    frames = []
    for line_number, line in enumerate(file, 1):
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
            frames.append(frame)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing line {line_number}: {e}", file=sys.stderr)
            sys.exit(1)
    return frames

def main() -> int:
    args = parse_args()
    frames = load_frames(args.session_file)
    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
