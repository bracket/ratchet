from math import pi
import numpy as np
import pyaudio
import time
from ratchet.scales import *

from functools import lru_cache

memoize = lru_cache()

CHANNELS = 1
RATE = 44100

def make_ramp(time):
    return np.linspace(0., time, time * RATE, dtype=np.float32)


def read_sample():
    with open('data/test.dat', 'rb') as fd:
        return np.frombuffer(fd.read(), dtype=np.int16).astype(dtype=np.float32) / 32768.


def plot_sample():
    import matplotlib.pyplot as plt
    from scipy import signal

    # sample = read_sample()[:RATE]
    sample = shifted_sample(0)[:RATE]

    f, t, Sxx = signal.spectrogram(
        sample,
        fs=44100,
        nperseg=2048,
    )

    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequencies [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


def low_c(time):
    from ratchet.scales import middle_major_octave
    c = middle_major_octave['c']
    low_c = c / 2.

    return np.sin(2. * pi * low_c * make_ramp(time))


def shifted_sample(steps):
    from scipy.interpolate import interp1d

    sample = read_sample()
    transform = np.fft.rfft(sample)

    smooth = interp1d(
        x = np.linspace(0., 1., len(transform), endpoint=True),
        y = transform,
        kind = 'linear',
        bounds_error = False,
        fill_value = complex(0, 0),
    )

    out = smooth(np.linspace(0., pow(2., -steps/12.), len(transform), endpoint=True))
    return np.fft.irfft(out, len(sample)).astype(dtype=np.float32)


def make_sample_scale():
    from ratchet.scales import c_major

    return {
        c : shifted_sample(steps)
        for c, steps
        in c_major.items()
    }

def test_note_parser():
    notes = r'''
        e4/4 d4/4 c4/4 d4/4
        e4/4 e4/4 e4/2
        d4/4 d4/4 d4/2
        e4/4 g4/4 g4/2
        e4/4 d4/4 c4/4 d4/4
        e4/4 e4/4 e4/4 e4/4
        d4/4 d4/4 e4/4 d4/4
        c4/1
    '''

    for note in parse_notes(notes):
        print(note)


@memoize
def make_adsr(duration):
    from scipy.interpolate import interp1d

    points = [
        (0., 0.),
        (.1, 1.),
        (.15, .75),
        ((duration - .1), .75),
        (duration, 0.),
    ]

    adsr = interp1d(
        x = [ p[0] for p in points ],
        y = [ p[1] for p in points ],
        kind = 'linear',
    )

    return adsr(np.linspace(0, duration, duration * RATE, endpoint=True))


def make_mary():
    from ratchet.scales import c_major

    notes = r'''
        e1 d1 c1 d1
        e1 e1 e2
        d1 d1 d2
        e1 g1 g2
        e1 d1 c1 d1
        e1 e1 e1 e1
        d1 d1 e1 d1
        c4
    '''

    quarter_note = .375

    notes = [
        (n[0], int(n[1]) * quarter_note)
        for n
        in notes.split()
    ]

    sample_scale = make_sample_scale()

    out = np.zeros(RATE * sum(d for _, d in notes), dtype=np.float32)

    env = make_adsr(4 * quarter_note) * (.5 / 3.)

    c_major = (sample_scale['c'] + sample_scale['e'] + sample_scale['g'])
    g_major = (sample_scale['g'] + sample_scale['b'] + sample_scale['d'])

    c_major = c_major[:len(env)] * env
    g_major = g_major[:len(env)] * env

    chords = [
        c_major,
        c_major,
        g_major,
        c_major,
        c_major,
        c_major,
        g_major,
        c_major
    ]

    offset = 0
    for chord in chords:
        start = offset
        end = offset = min(start + len(chord), len(out))
        out[start:end] += chord

        if end >= len(out): break

    offset = 0

    for note, duration in notes:
        env = make_adsr(duration)
        sample = sample_scale[note][:len(env)] * env

        out[offset:offset + len(sample)] += sample
        offset += len(sample)

    return out


def main():
    pa = pyaudio.PyAudio()

    # sample = shifted_sample(0.)
    sample = make_mary()

    current_offset = [ 0 ]

    def callback(in_data, frame_count, time_info, status):
        start = current_offset[0]
        end = current_offset[0] = start + frame_count

        return (sample[start:end], pyaudio.paContinue)
        
    stream = pa.open(
        format = pyaudio.paFloat32,
        channels = CHANNELS,
        rate = RATE,
        stream_callback = callback,
        output = True,
    )

    stream.start_stream()

    while stream.is_active():
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()

    pa.terminate()


if __name__ == '__main__':
    main()
