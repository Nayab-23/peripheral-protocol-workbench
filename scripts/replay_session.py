#!/usr/bin/env python3
import argparse
import json
import sys
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay

def load_frames_from_file(file_path: str) -> list[Frame]:
    frames = []
    with open(file_path, "r", encoding="utf-8") as f:
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
                print(f"Warning: skipping invalid frame line: {line} ({e})", file=sys.stderr)
    return frames

def print_frame_summary(frame: Frame) -> None:
    payload_preview = frame.payload[:20].hex() + ("..." if len(frame.payload) > 20 else "")
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload_len={len(frame.payload)} payload_hex={payload_preview}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the session file containing captured frames in JSON lines format.")
    parser.add_argument("--inject-bad-checksum", action="store_true", help="Inject bad checksum errors during replay.")
    args = parser.parse_args()

    frames = load_frames_from_file(args.session_file)
    if not frames:
        print(f"No valid frames loaded from {args.session_file}", file=sys.stderr)
        return 1

    replay_generator = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_generator):
        print(result)

    print("\nFrame summaries:")
    for frame in frames:
        print_frame_summary(frame)

    return 0

if __name__ == "__main__":
    sys.exit(main())
