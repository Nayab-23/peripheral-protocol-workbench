#!/usr/bin/env python3
import argparse
import json
import sys

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(path: str) -> list[Frame]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    frames = []
    for item in data:
        # Expecting dicts with keys: message_type, sequence, payload (base64 or hex string)
        # For simplicity, assume payload is hex string
        payload_bytes = bytes.fromhex(item["payload"])
        frame = Frame(
            message_type=item["message_type"],
            sequence=item["sequence"],
            payload=payload_bytes,
        )
        frames.append(frame)
    return frames


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
        frames = load_frames_from_file(args.session_file)
    except Exception as e:
        print(f"Error loading session file: {e}", file=sys.stderr)
        return 1

    results = validate_replay(replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum))
    for result in results:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
