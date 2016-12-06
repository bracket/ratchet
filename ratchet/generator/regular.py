from .sound_generator import SoundGenerator
from collections import namedtuple
import numpy as np

__all__ = [
    'RegularGenerator'
]

class RegularGenerator(SoundGenerator):
    def __init__(self, source_generator, queue_frame_count = 1024):
        super().__init__(source_generator.frame_rate)

        self.source_generator = source_generator
        self.generator = None
        self.queue = [ ]
        self.last_start = None
        self.last_end = 0
        self.queue_frame_count = queue_frame_count


    def prime_queue(self, frame_count):
        self.extend_queue()

        while self.last_start < frame_count:
                self.extend_queue()


    def extend_queue(self):
        if self.generator is None:
            self.generator = self.source_generator.start()

        sample = self.generator.send(self.queue_frame_count)
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
        frame_count = yield None
        
        queue = self.queue
        current = Interval(0, frame_count)
        ping = pong = None

        entry = queue.pop(0)

        while True:
            while entry.interval.end < current.start:
                entry = queue.pop(0)

            ping = resize_output_sample(ping, entry.sample, current.length())
            intersection = current.intersection(entry.interval)

            while intersection.length() > 0:
                source_slice = intersection.shift(-entry.interval.start).slice()
                target_slice = intersection.shift(-current.start).slice()

                ping[:,target_slice] = entry.sample[:,source_slice]

                ping_filled = current.end <= entry.interval.end

                if ping_filled:
                    frame_count = yield ping
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


class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


    def length(self):
        return self.end - self.start


    def intersection(self, other):
        return Interval(max(self.start, other.start), min(self.end, other.end))


    def shift(self, amount):
        return Interval(self.start + amount, self.end + amount)


    def slice(self):
        return slice(self.start, self.end)


    def __repr__(self):
        return 'Interval({}, {})'.format(self.start, self.end)


QueueEntry = namedtuple('QueueEntry', [ 'interval', 'channels', 'frame_count', 'sample' ])
