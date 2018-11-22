from .sound_generator import SoundGenerator
import numpy as np

class SineGenerator(SoundGenerator):
    '''
    Generates a fixed size block corresponding to some number of periods of a sine wave.
    '''


    def __init__(self, frame_rate, hertz, amplitude, base_length_in_seconds=1.):
        '''
        frame_rate
            Frame rate requests in frames per second

        hertz : float
            Frequency of requested sine wave in hertz

        amplitude : float
            Amplitude to scale wave to before output

        base_length_in_seconds, optional
            Suggestion for the length of the block which is repeatedly yielded.
            The length will be adjusted so that an integral periods fit within.
        '''

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

        abscissae = np.linspace(0, total_radians, length_in_frames, endpoint=False)
        ordinates = np.sin(abscissae, dtype=np.float32)
        ordinates *= self.amplitude

        while True:
            yield ordinates
