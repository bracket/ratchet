from .sound_generator import SoundGenerator
from .regular import make_regular_generator

class Adder(SoundGenerator):
    def __init__(self, frame_rate, generators, frame_count = 1024):
        super().__init__(frame_rate)

        self.generators = [
            make_regular_generator(g, frame_count)
            for g
            in generators
        ]

        self.frame_count = frame_count


    def __iter__(self):
        for g in self.generators:
            g.prime_queue(self.frame_count)

        gens = [ g.start() for g in self.generators ]
        first = gens.pop(0)

        _ = yield

        while True:
            out = first.send(self.frame_count)

            for g in gens:
                frame = g.send(self.frame_count)
                out += frame

            _ = yield out

            for g in self.generators:
                if not g.queue:
                    g.extend_queue()
