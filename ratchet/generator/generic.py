from .sound_generator import SoundGenerator

class GenericGenerator(SoundGenerator):
    def __init__(self, frame_rate, generator):
        super().__init__(frame_rate)
        self.generator = generator

    def __iter__(self):
        yield from self.generator
