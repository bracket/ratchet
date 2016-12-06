import numpy as np

def make_silent_generator(frame_count, frame_rate):
    from ratchet.generator.generic import GenericGenerator

    empty = np.zeros(frame_count, dtype=np.float32)

    def source_generator():
        while True:
            yield empty

    return GenericGenerator(source_generator(), frame_rate)


def test_regular_generator_single_channel():
    from ratchet.generator.regular import RegularGenerator

    source_generator = make_silent_generator(64, 44100)

    generator = RegularGenerator(source_generator)
    g = generator.start()
    last_end = 0

    for expected_frame_count in range(10, 101, 10):
        last_end += expected_frame_count

        while generator.last_end < last_end:
            generator.extend_queue()

        sample = g.send(expected_frame_count)
        actual_channels, actual_frame_count = sample.shape

        assert actual_channels == 1
        assert actual_frame_count == expected_frame_count
        assert not np.any(sample)


def test_sine_generator():
    from ratchet.generator.sine import SineGenerator

    generator = SineGenerator(44100, 440, .5)
    sample = generator.start().send(0)

    epsilon = 1e-4

    assert abs(np.max(sample) - 0.5) < epsilon
    assert abs(np.min(sample) + 0.5) < epsilon
    assert abs(np.mean(sample)) < epsilon


def test_pyaudio():
    from ratchet.runner import pyaudio
