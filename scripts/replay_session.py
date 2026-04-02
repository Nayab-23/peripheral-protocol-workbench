#!/usr/bin/env python3
import argparse
import json
import sys
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay

def load_session(filename: str) -> list[Frame]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    frames = []
    for item in data:
        # Expecting dicts with keys: message_type, sequence, payload (base64 or hex string)
        # For simplicity, assume payload is hex string
        payload_bytes = bytes.fromhex(item["payload"])
        frame = Frame(
            message_type=item["message_type"],
            sequence=item["sequence"],
            payload=payload_bytes
        )
        frames.append(frame)
    return frames

def print_frame_summary(frame: Frame) -> None:
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload_len={len(frame.payload)} payload={frame.payload.hex()}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the JSON session file containing frames")
    parser.add_argument("--inject-bad-checksum", action="store_true", help="Inject bad checksum during replay")
    args = parser.parse_args()

    try:
        frames = load_session(args.session_file)
    except Exception as e:
        print(f"Error loading session file: {e}", file=sys.stderr)
        return 1

    results = validate_replay(replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum))
    for result in results:
        print(result)

    print("\nFrame summaries:")
    for frame in frames:
        print_frame_summary(frame)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
