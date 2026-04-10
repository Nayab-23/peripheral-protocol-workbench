#!/usr/bin/env python3
import argparse
import json
import sys

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_session_frames(path: str) -> list[Frame]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    frames = []
    for item in data:
        # Expecting dict with keys: message_type, sequence, payload (base64 or hex string)
        # Here assume payload is hex string
        payload_bytes = bytes.fromhex(item.get("payload", ""))
        frame = Frame(
            message_type=item["message_type"],
            sequence=item["sequence"],
            payload=payload_bytes,
        )
        frames.append(frame)
    return frames


def print_frame_summary(frame: Frame) -> None:
    # Print a concise summary of the frame
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload_len={len(frame.payload)} payload={frame.payload!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the JSON file containing captured frames")
    parser.add_argument(
        "--inject-bad-checksum",
        action="store_true",
        help="Inject bad checksum errors during replay for testing",
    )

    args = parser.parse_args()

    try:
        frames = load_session_frames(args.session_file)
    except Exception as e:
        print(f"Error loading session file: {e}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        # result is a Frame or an error description
        if isinstance(result, Frame):
            print_frame_summary(result)
        else:
            # Print error info
            print(f"Error: {result}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
