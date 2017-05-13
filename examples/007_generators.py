from ratchet.generator.sine import SineGenerator
from ratchet.generator.adder import Adder

from ratchet.runner import PyAudioRunner
from ratchet.runner import FileWriter

from math import pow

import numpy as np

def overtones(fundamental):
    i = 1
    f = i * fundamental

    while f < 20e3:
        yield f
        # yield 5 * f / 4
        # yield 3 * f / 2
        i += 1
        f = i * fundamental


def main():
    p = 1
    k = 2
    amplitudes = np.array([ (-1)**(n - 1) / (n ** p) if not ((n - 1) % k) else 0 for n in range(1, 30) ], dtype=np.float32)
    print(amplitudes)

    amplitudes /= np.absolute(amplitudes).sum()

    fundamental = 110. * pow(2, 3/12) # c3

    frequencies = list(overtones(fundamental))[:len(amplitudes)]

    generators = [
        SineGenerator(44100, f, .6 * a, .05)
        for f, a in zip(frequencies, amplitudes)
    ]

    generator = Adder(44100, generators)

    # runner = FileWriter('adder.caff')
    runner = PyAudioRunner()

    runner.run(generator)


if __name__ == '__main__':
    main()
