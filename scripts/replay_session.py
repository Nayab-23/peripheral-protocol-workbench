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

def main() -> int:
    args = parse_args()
    frames = []
    for line_number, line in enumerate(args.session_file, start=1):
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
            frames.append(Frame(message_type=mt, sequence=seq, payload=payload_bytes))
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing line {line_number}: {e}", file=sys.stderr)
            return 1

    for result in validate_replay(replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)):
        print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
