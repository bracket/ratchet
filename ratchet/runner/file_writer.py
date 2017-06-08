from .runner import Runner
from pathlib import Path

import numpy as np

class FileWriter(Runner):
    def __init__(self, path):
        self.path = Path(path).with_suffix('.caff')


    def run(self, generator):
        import aifc

        initialized = False
        g = generator.start()

        with aifc.open(str(self.path), 'wb') as out:
            while True:
                try:
                    sample = next(g)
                except StopIteration:
                    return

                if not initialized:
                    channels, frame_count = sample.shape
                    out.setframerate(generator.frame_rate)
                    out.setnchannels(channels)
                    out.setsampwidth(2)
                    initialized = True

                sample = (sample * (2 ** 15 - 1)).astype(dtype='>i2')
                out.writeframes(sample.tobytes())
