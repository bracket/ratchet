import numpy as np

from .sound_generator import SoundGenerator

class Microphone(SoundGenerator):
    def __init__(self, frame_rate, channels=1, chunk_size=256):
        super().__init__(frame_rate)

        self.channels = channels
        self.chunk_size = chunk_size
        self.stream = None


    def __iter__(self):
        import pyaudio

        dtypes = {
            pyaudio.paInt8  : np.int8,
            pyaudio.paInt16 : np.int16,
            pyaudio.paInt24 : None,
            pyaudio.paInt32 : np.int32,
        }

        width = 2

        format = pyaudio.get_format_from_width(width)
        dtype = dtypes[format]

        pa = pyaudio.PyAudio() 
        samples = [ ]

        shape = (self.channels, self.chunk_size)

        empty = np.zeros(shape=(self.channels, self.chunk_size), dtype=np.float32)

        def callback(in_data, frame_count, time_info, status):
            shape = (self.channels, frame_count)

            array = np.frombuffer(in_data, dtype)
            samples.append(array.reshape(shape).astype(np.float32)/32768.)
            
            return (in_data, pyaudio.paContinue)

        yield

        self.stream = pa.open(
            format=format,
            rate=self.frame_rate,
            channels=self.channels,
            input=True,
            output=False,
            # stream_callback=callback,
            frames_per_buffer=self.chunk_size,
        )

        self.stream.start_stream()

        while self.stream.is_active() or samples:
            in_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            array = np.frombuffer(in_data, dtype)
            yield array.reshape(shape).astype(np.float32)/32768.

            # try:
            #     yield samples.pop(0)
            # except:
            #     yield empty
