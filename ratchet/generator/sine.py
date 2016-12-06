from .sound_generator import SoundGenerator
import numpy as np

class SineGenerator(SoundGenerator):
    def __init__(self, frame_rate, hertz, amplitude, base_length_in_seconds=1.):
        super().__init__(frame_rate)
        self.hertz = hertz
        self.amplitude = amplitude
        self.base_length_in_seconds = base_length_in_seconds

    def __iter__(self):
        from math import pi, ceil

        tau = 2 * pi

        radians_per_second = tau * self.hertz
        total_radians = self.base_length_in_seconds * radians_per_second
        total_radians = ceil(total_radians / tau) * tau

        length_in_seconds = total_radians / radians_per_second
        length_in_frames = int(ceil(length_in_seconds * self.frame_rate))

        abscissae = np.linspace(0, total_radians, length_in_frames, endpoint=True)
        ordinates = np.sin(abscissae, dtype=np.float32)
        ordinates *= self.amplitude

        _ = yield

        while True:
            _ = yield ordinates
