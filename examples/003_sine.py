import pyaudio
import numpy as np
from math import pi

WIDTH = 2
CHANNELS = 2
RATE = 44100

def make_ramp(time):
    return np.linspace(0., 1.,  time * RATE, dtype=np.float32)


def make_sample(frequency, amplitude = .5, slide = 1.):
    if slide != 1.:
        ramp = frequency * np.power(make_ramp(1.), slide)
    else:
        ramp = frequency * make_ramp(1.)

    xs = 2. * pi * ramp
    ys = amplitude * np.sin(xs)

    return ys


def make_noise():
    return (np.random.random(RATE) - .5) * 2


chromatic = { i : pow(2., i / 12.) for i in range(12) }
major = [ 0, 2, 4, 5, 7, 9, 11 ]

def generate_data():
    start_sample = make_sample(110, 1.5, 2.)
    end_sample = make_sample(440, 1.5, 2.)
    # end_sample = .5 * make_noise()


    # start_sample, end_sample = end_sample, start_sample

    # start_sample = make_sample(440, 1., 1.)
    # end_sample = make_sample(110, 1., 1.)

    slide = make_ramp(1.)
    sample = (1 - slide) * start_sample + slide * end_sample
    # sample = end_sample

    shape = sample.shape + (2,)

    xfade = (1 + np.sin(40 * 2. * pi * make_ramp(1))) / 2

    out = np.zeros(dtype=np.float32, shape=shape)
    out[:,0] = xfade * sample
    out[:,1] = (1 - xfade) * sample

    return bytes(out.data)

def main():
    pa = pyaudio.PyAudio()

    sample = generate_data()

    stream = pa.open(
        format = pyaudio.paFloat32,
        channels = WIDTH,
        rate = RATE,
        output = True,
    )

    stream.write(sample)

    stream.stop_stream()
    stream.close()

    pa.terminate()


if __name__ == '__main__':
    main()
