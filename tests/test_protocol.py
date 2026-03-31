from peripheral_protocol_workbench.protocol import Frame, decode_frame, encode_frame, StreamParser
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


def test_stream_parser_partial_frame() -> None:
    parser = StreamParser()
    frame = Frame(message_type=3, sequence=42, payload=b"hello")
    encoded = encode_frame(frame)

    # Feed partial data, no frames yet
    parts = [encoded[:3], encoded[3:5], encoded[5:]]
    results = []
    for part in parts:
        results.extend(parser.feed(part))
    assert len(results) == 1
    assert results[0] == frame


def test_stream_parser_noise_resync() -> None:
    parser = StreamParser()
    frame = Frame(message_type=4, sequence=7, payload=b"data")
    encoded = encode_frame(frame)

    noise = b"\x00\xFF\x01\x02"
    data = noise + encoded
    frames = list(parser.feed(data))
    assert len(frames) == 1
    assert frames[0] == frame


def test_stream_parser_recovery_after_bad_checksum() -> None:
    parser = StreamParser()
    good_frame1 = Frame(message_type=5, sequence=10, payload=b"ok1")
    good_frame2 = Frame(message_type=5, sequence=11, payload=b"ok2")
    encoded1 = encode_frame(good_frame1)
    encoded2 = encode_frame(good_frame2)

    # Create a bad frame by corrupting checksum
    bad_frame = bytearray(encoded1)
    bad_frame[-1] ^= 0xFF  # corrupt checksum

    data = bytes(bad_frame) + encoded2

    frames = list(parser.feed(data))
    # Should skip bad frame and yield only the second good frame
    assert len(frames) == 1
    assert frames[0] == good_frame2
