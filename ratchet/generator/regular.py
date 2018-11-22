from .sound_generator import SoundGenerator

import numpy as np

__all__ = [
    'RegularGenerator',
    'make_regular_generator',
]

class RegularGenerator(SoundGenerator):
    ''' Regularized chunk length of other generators

        SoundGenerators are not required to supply the same number of frames
        each time they yield, which can make some operations difficult when
        dealing with chunks from multiple generators.  RegularGenerator takes
        an arbitrary source generator and replaces it with a generator which
        yields chunks of a fixed size.
    '''

    def __init__(self, source_generator, chunk_size = 1024):
        '''
            source_generator
                generator whose chunks are to be regularized.  frame_rate is
                taken from this generator.

            chunk_size
                number of frames yield with each chunk
        '''
        super().__init__(source_generator.frame_rate)

        self.source_generator = source_generator
        self.generator = iter(self.source_generator)
        self.chunk_size = chunk_size

        self.in_block = None
        self.in_start = 0

        self.out_block = None
        self.out_start = 0

    @property
    def in_end(self):
        if self.in_block is None:
            return 0

        channels, frame_count = self.in_block.shape

        return self.in_start + frame_count

    @property
    def out_end(self):
        if self.out_block is None:
            return 0

        channels, frame_count = self.out_block.shape

        return self.out_start + frame_count


    def underflow(self):
        if self.in_block is not None:
            channels, frame_count = self.in_block.shape
            self.in_start += frame_count

        self.in_block = sample = next(self.generator)

        shape = sample.shape

        if len(shape) == 1:
            shape = (1, shape[0])
        elif len(shape) != 2:
            raise RuntimeError('invalid shape for generator output', { 'shape' : shape })

        if shape != sample.shape:
            self.in_block = sample.reshape(shape)

        if self.out_block is None:
            channels, frame_count = shape
            self.out_block = np.zeros(dtype=sample.dtype, shape=(channels, self.chunk_size))


    def __iter__(self):
        frames_copied = 0

        while True:
            while frames_copied <= self.out_end:
                start = max(self.in_start, self.out_start)
                end   = min(self.in_end, self.out_end)

                if end <= start:
                    try:
                        self.underflow()
                        continue
                    except StopIteration:
                        if self.out_block is not None:
                            yield self.out_block
                        raise

                self.out_block[:,start - self.out_start:end - self.out_start] = (
                    self.in_block[:,start - self.in_start:end - self.in_start]
                )

                frames_copied += (end - start)

            yield self.out_block

            self.out_block[:,:] = 0.
            self.out_start += self.chunk_size


# TODO: This probably doesn't really do what I think the it does.

def make_regular_generator(g, chunk_size):
    if isinstance(g, RegularGenerator):
        if g.chunk_size == chunk_size:
            return g
        else:
            return RegularGenerator(g.source_generator, chunk_size)

    return RegularGenerator(g, chunk_size)
