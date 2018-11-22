import pyaudio
import time
import numpy as np

WIDTH = 2
CHANNELS = 1
RATE = 44100

def main():
    pa = pyaudio.PyAudio()

    # fd = open('data/test.dat', 'wb')

    def callback(in_data, frame_count, time_info, status):
        # print(np.frombuffer(in_data, dtype=np.int16))
        # fd.write(in_data)
        # print(frame_count)
        return (in_data, pyaudio.paContinue)

    format = pa.get_format_from_width(WIDTH)

    stream = pa.open(
        format = format,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        output = True,
        stream_callback = callback,
        frames_per_buffer=256,
    )

    stream.start_stream()

    while stream.is_active():
        time.sleep(0.0025)

    stream.stop_stream()
    stream.close()

    pa.terminate()

if __name__ == '__main__':
    main()
