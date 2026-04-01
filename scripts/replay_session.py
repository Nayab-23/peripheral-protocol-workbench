#!/usr/bin/env python3
import argparse
import json
import sys
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay

def load_frames_from_file(filename: str) -> list[Frame]:
    frames = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                frame = Frame(
                    message_type=data["message_type"],
                    sequence=data["sequence"],
                    payload=bytes.fromhex(data["payload"]),
                )
                frames.append(frame)
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"Skipping invalid frame line: {line} ({e})", file=sys.stderr)
    return frames

def print_frame_summary(frame: Frame) -> None:
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload={frame.payload.hex()} length={len(frame.payload)}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the session capture file (JSON lines format)")
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors during replay",
    )
    args = parser.parse_args()

    frames = load_frames_from_file(args.session_file)
    if not frames:
        print(f"No valid frames loaded from {args.session_file}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        # result is a tuple (frame, is_valid_checksum)
        frame, valid = result
        print_frame_summary(frame)
        print(f"  Checksum valid: {valid}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
