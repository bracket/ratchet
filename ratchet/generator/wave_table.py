import numpy as np

from .sound_generator import SoundGenerator

class WaveTable(SoundGenerator):
    def __init__(self, frame_rate, wave_table):
        super().__init__(frame_rate)

        self.wave_table = reshape_wave_table(wave_table)


    def __iter__(self):
        channels, frames = self.wave_table.shape

        middle = int((frames + 1) / 2)
        ramp = np.linspace(0, 1, middle, endpoint=True)

        envelope = np.zeros((channels, frames), dtype=np.float32)

        if frames % 2:
            envelope[:,:middle] = ramp
            envelope[:,middle:] = ramp[-2::-1]
        else:
            envelope[:,:middle] = ramp
            envelope[:,middle:] = ramp[::-1]

        table = envelope * self.wave_table
        table += np.concatenate([ table[:,middle:], table[:,:middle] ], axis=1)

        while True:
            yield table
            # yield self.wave_table


def reshape_wave_table(wave_table):
    shape = wave_table.shape

    if not isinstance(shape, tuple):
        shape = (1, shape)
    elif len(shape) == 1:
        shape = (1,) + shape

    return wave_table.reshape(shape)
