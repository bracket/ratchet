from ..interval import Interval
from .sound_generator import SoundGenerator
from collections import namedtuple

import numpy as np

__all__ = [
    'RegularGenerator',
    'make_regular_generator',
]

QueueEntry = namedtuple('QueueEntry', [ 'interval', 'channels', 'frame_count', 'sample' ])

class RegularGenerator(SoundGenerator):
    ''' Regularized chunk length of other generators

        SoundGenerators are not required to supply the same number of frames
        each time they yield, which can make some operations difficult to when
        dealing with chunks from multiple generators.  RegularGenerator takes
        an arbitrary source generator and replaces with a generator which
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
        self.generator = None
        self.queue = [ ]
        self.last_start = None
        self.last_end = 0
        self.chunk_size = chunk_size


    def prime_queue(self):
        self.extend_queue()

        while self.last_start < self.chunk_size:
                self.extend_queue()


    def extend_queue(self):
        if self.generator is None:
            self.generator = self.source_generator.start()

        sample = next(self.generator)
        shape = sample.shape

        if len(shape) == 1:
            shape = (1, shape[0])
        elif len(shape) != 2:
            raise RuntimeError('invalid shape for generator output', { 'shape' : shape })

        if shape != sample.shape:
            sample = sample.reshape(shape)

        channels, frame_count = sample.shape

        self.last_start, self.last_end = self.last_end, self.last_end + frame_count
        self.queue.append(QueueEntry(Interval(self.last_start, self.last_end), channels, frame_count, sample))


    def __iter__(self):
        yield None

        queue = self.queue
        frame_count = self.chunk_size

        current = Interval(0, frame_count)
        ping = pong = None

        entry = queue.pop(0)

        while True:
            while entry.interval.end <= current.start:
                entry = queue.pop(0)

            ping = resize_output_sample(ping, entry.sample, current.length())
            intersection = current.intersection(entry.interval)

            while intersection.length() > 0:
                source_slice = intersection.shift(-entry.interval.start).slice()
                target_slice = intersection.shift(-current.start).slice()

                ping[:,target_slice] = entry.sample[:,source_slice]

                ping_filled = current.end <= entry.interval.end

                if ping_filled:
                    # TODO: Temporary fix for double buffering messing up.
                    # This class needs more testing and documentation

                    yield ping.copy()
                    current = Interval(current.end, current.end + frame_count)
                    ping, pong = pong, ping
                    ping = resize_output_sample(ping, entry.sample, current.length())
                else:
                    entry = queue.pop(0)

                intersection = current.intersection(entry.interval)


def resize_output_sample(output_sample, source_sample, new_frame_count):
    source_channels, source_frame_count = source_sample.shape

    if output_sample is None:
        return np.zeros(shape=(source_channels, new_frame_count), dtype=source_sample.dtype)

    output_channels, output_frame_count = output_sample.shape

    if output_frame_count < new_frame_count:
        output_sample.resize((source_channels, new_frame_count), refcheck=False)

    return output_sample


def make_regular_generator(g, chunk_size):
    if isinstance(g, RegularGenerator):
        if g.chunk_size == chunk_size:
            return g
        else:
            return RegularGenerator(g.source_generator, chunk_size)

    return RegularGenerator(g, chunk_size)
