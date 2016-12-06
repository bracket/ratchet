from ratchet.generator.sine import SineGenerator
from ratchet.runner import pyaudio

def main():
    generator = SineGenerator(44100, 440., .5)
    pyaudio.run(generator)


if __name__ == '__main__':
    main()
