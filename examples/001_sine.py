''' Setup a basic PyAudio runner with a SineGenerator.

'''

from ratchet.generator import SineGenerator
from ratchet.runner import PyAudioRunner

CHANNELS = 2
FRAME_RATE = 44100


def main():
    sine = SineGenerator(FRAME_RATE, 440., 1., 2.)
    runner = PyAudioRunner()

    runner.run(sine)


if __name__ == '__main__':
    main()
