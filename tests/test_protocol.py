from peripheral_protocol_workbench.protocol import Frame, decode_frame, encode_frame
from peripheral_protocol_workbench.simulator import replay_frames, validate_replay


def test_encode_decode_round_trip() -> None:
    frame = Frame(message_type=2, sequence=17, payload=b"abc")
    encoded = encode_frame(frame)
    decoded = decode_frame(encoded)
    assert decoded == frame


def test_replay_fault_injection() -> None:
    frames = [Frame(message_type=1, sequence=1, payload=b"x"), Frame(message_type=1, sequence=2, payload=b"y")]
    results = validate_replay(replay_frames(frames, inject_bad_checksum=True))
    assert results[0] == "ok:1"
    assert results[1].startswith("error:")
