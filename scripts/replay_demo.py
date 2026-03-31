#!/usr/bin/env python3
from peripheral_protocol_workbench.protocol import Frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def main() -> int:
    frames = [
        Frame(message_type=0x10, sequence=1, payload=b"led:on"),
        Frame(message_type=0x20, sequence=2, payload=b"temp:24.7"),
    ]
    for result in validate_replay(replay_frames(frames, inject_bad_checksum=True)):
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
