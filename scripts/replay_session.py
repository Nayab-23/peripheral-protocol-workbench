#!/usr/bin/env python3
import argparse
import json
import sys

from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def load_session_frames(session_file_path: str) -> list[Frame]:
    frames = []
    with open(session_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                # Expecting dict with keys: message_type, sequence, payload (base64 or hex)
                # For simplicity, assume payload is hex string
                message_type = data.get("message_type")
                sequence = data.get("sequence")
                payload_hex = data.get("payload")
                if message_type is None or sequence is None or payload_hex is None:
                    print(f"Skipping invalid frame line: {line}", file=sys.stderr)
                    continue
                payload = bytes.fromhex(payload_hex)
                frame = Frame(message_type=message_type, sequence=sequence, payload=payload)
                frames.append(frame)
            except Exception as e:
                print(f"Error parsing line: {line} - {e}", file=sys.stderr)
    return frames


def print_frame_summary(frame: Frame) -> None:
    # Print a concise summary of the frame
    print(f"Frame seq={frame.sequence} type=0x{frame.message_type:02X} payload_len={len(frame.payload)} payload={frame.payload!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a captured serial protocol session and print frame summaries.")
    parser.add_argument("session_file", help="Path to the session file containing captured frames in JSON lines format.")
    parser.add_argument("--inject-bad-checksum", action="store_true", help="Inject bad checksum errors during replay.")

    args = parser.parse_args()

    frames = load_session_frames(args.session_file)
    if not frames:
        print(f"No valid frames loaded from {args.session_file}", file=sys.stderr)
        return 1

    replay_iter = replay_frames(frames, inject_bad_checksum=args.inject_bad_checksum)
    for result in validate_replay(replay_iter):
        # result is expected to be a Frame or error info
        if isinstance(result, Frame):
            print_frame_summary(result)
        else:
            # Could be error or diagnostic info
            print(f"Replay result: {result}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
