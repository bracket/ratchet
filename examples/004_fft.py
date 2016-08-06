import pyaudio
import numpy as np
from math import pi

WIDTH = 1
CHANNELS = 2
RATE = 44100

def make_ramp(time):
    return np.linspace(0, 1, time * RATE, dtype=np.float32)


def make_sample(frequency):
    return np.sin(2. * pi * frequency * make_ramp(1.))


def make_envelope():
    from scipy.interpolate import interp1d

    points = [
        (0., 0.),
        (.1, 1.),
        (.15, .5),
        (.7, .5),
        (1., 0.),
    ]

    return interp1d(
       x = [ p[0] for p in points ],
       y = [ p[1] for p in points ],
       kind = 'linear'
    )

def make_spectrum():
    from scipy.interpolate import interp1d

    base = [
        (0.,        0.),
        (440 - .5,  0.),
        (440.,      1.),
        (440. + .5, 0.),
        (44100., 0.)
    ]

    return interp1d(
        x = [ b[0] for b in base ],
        y = [ complex(RATE * b[1], 0.) for b in base ],
        kind = 'linear',
    )


def plot(xs, ys):
    import matplotlib.pyplot as plt
    plt.plot(xs, ys)
    plt.show()


def main():
    from numpy.fft import rfft, irfft

    ramp = make_ramp(1.)
    env = make_envelope()

    bank = make_spectrum()

    transform = bank(np.linspace(0, RATE/2, RATE/2 + 1, endpoint=True))

    pa = pyaudio.PyAudio()

    # transform = np.zeros(RATE/2 + 1, dtype=np.complex64)
    # transform = np.zeros(RATE/2 + 1, dtype=np.complex64)

    # amp = 1
    # for freq in range(1, 4):
    #     transform[220 * freq]  = complex(amp, 0) * RATE
    #     amp *= .5

    sample = irfft(transform, RATE)

    stream = pa.open(
        format = pyaudio.paFloat32,
        channels = CHANNELS,
        rate = RATE,
        output = True
    )

    stream.write(sample.astype(np.float32))

    stream.stop_stream()
    stream.close()

    pa.terminate()


if __name__ == '__main__':
    main()
