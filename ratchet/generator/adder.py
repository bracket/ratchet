from .sound_generator import SoundGenerator
from .regular import make_regular_generator

class Adder(SoundGenerator):
    def __init__(self, frame_rate, generators, chunk_size = 1024):
        super().__init__(frame_rate)

        self.generators = [
            make_regular_generator(g, chunk_size)
            for g
            in generators
        ]

        self.chunk_size = chunk_size


    def __iter__(self):
        for g in self.generators:
            g.prime_queue()

        gens = [ g.start() for g in self.generators ]
        first = gens.pop(0)

        yield None

        while True:
            out = first.send(self.frame_count)

            for g in gens:
                frame = next(g)
                out += frame

            yield out

            for g in self.generators:
                if not g.queue:
                    g.extend_queue()
