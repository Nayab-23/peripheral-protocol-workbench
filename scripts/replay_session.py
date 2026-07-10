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
        help="Path to the JSON lines session file",
    )
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors into replayed frames",
    )
    return parser.parse_args()

def load_frames(file) -> list[Frame]:
    frames = []
    for line in file:
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
            payload = bytes.fromhex(payload_hex)
            frames.append(Frame(message_type=mt, sequence=seq, payload=payload))
        except Exception as e:
            print(f"Error parsing line: {line} - {e}", file=sys.stderr)
    return frames

def print_frame_summary(frame: Frame) -> None:
    # Print a concise summary of the frame
    payload_preview = frame.payload.decode(errors='replace')
    if len(payload_preview) > 40:
        payload_preview = payload_preview[:37] + "..."
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload='{payload_preview}' checksum_valid={frame.checksum_valid}")

def main() -> int:
    args = parse_args()
    frames = load_frames(args.session_file)
    if not frames:
        print("No valid frames loaded from session file.", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        print_frame_summary(result.frame)
        if result.error:
            print(f"  Error: {result.error}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
