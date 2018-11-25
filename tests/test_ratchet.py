import numpy as np

def make_silent_generator(frame_count, frame_rate):
    from ratchet.generator.generic import GenericGenerator

    empty = np.zeros(frame_count, dtype=np.float32)

    def source_generator():
        while True:
            yield empty

    return GenericGenerator(frame_rate, source_generator())


def test_regular_generator_single_channel():
    from ratchet.generator.regular import RegularGenerator

    source_generator = make_silent_generator(7, 44100)

    generator = RegularGenerator(source_generator, 8)

    r = range(0, 56, 8)

    for i, b in zip(r, iter(generator)):
        channels, frame_count = b.shape

        assert channels == 1
        assert frame_count == 8


def test_sine_generator():
    from ratchet.generator.sine import SineGenerator

    generator = SineGenerator(44100, 440, .5)
    sample = next(iter(generator))

    epsilon = 1e-4

    assert abs(np.max(sample) - 0.5) < epsilon
    assert abs(np.min(sample) + 0.5) < epsilon
    assert abs(np.mean(sample)) < epsilon


def test_pyaudio():
    from ratchet.runner import pyaudio
