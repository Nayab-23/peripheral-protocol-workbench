#!/usr/bin/env python3
import argparse
import json
import sys
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay a captured serial protocol session and print frame summaries."
    )
    parser.add_argument(
        "session_file",
        type=argparse.FileType('r'),
        help="Path to the JSON lines session file to replay",
    )
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors during replay",
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
            # Validate keys
            if not all(k in obj for k in ("message_type", "sequence", "payload")):
                print(f"Skipping line {line_number}: missing required keys", file=sys.stderr)
                continue
            # Convert payload hex string to bytes
            payload_bytes = bytes.fromhex(obj["payload"])
            frame = Frame(
                message_type=obj["message_type"],
                sequence=obj["sequence"],
                payload=payload_bytes,
            )
            frames.append(frame)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Skipping line {line_number}: invalid format ({e})", file=sys.stderr)
    return frames

def main() -> int:
    args = parse_args()
    frames = load_frames(args.session_file)
    if not frames:
        print("No valid frames loaded from session file.", file=sys.stderr)
        return 1

    # Replay frames with optional fault injection
    replayed = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)

    # Validate replay and print results
    for result in validate_replay(replayed):
        print(result)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
