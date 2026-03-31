#!/usr/bin/env python3
import argparse
import json
from typing import List

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_frames_from_file(path: str) -> List[Frame]:
    frames = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                # Expecting dict with keys: message_type, sequence, payload (base64 or hex string)
                # For simplicity, assume payload is hex string
                message_type = data["message_type"]
                sequence = data["sequence"]
                payload_hex = data["payload"]
                payload = bytes.fromhex(payload_hex)
                frame = Frame(message_type=message_type, sequence=sequence, payload=payload)
                frames.append(frame)
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"Skipping invalid frame line: {line} ({e})")
    return frames


def print_frame_summary(frame: Frame) -> None:
    # Print a concise summary of the frame
    payload_preview = frame.payload[:20]
    payload_display = payload_preview.hex() + ("..." if len(frame.payload) > 20 else "")
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload_len={len(frame.payload)} payload={payload_display}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the captured session file (JSON lines format)")
    parser.add_argument("--inject-bad-checksum", action="store_true", help="Inject bad checksum errors during replay")
    args = parser.parse_args()

    frames = load_frames_from_file(args.session_file)
    if not frames:
        print("No valid frames loaded from session file.")
        return 1

    print(f"Loaded {len(frames)} frames from {args.session_file}")

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    validation_iter = validate_replay(replay_iter)

    for result in validation_iter:
        # result is expected to be a string summary or validation message
        print(result)

    print("Replay complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
