from ..generator.regular import make_regular_generator
from .runner import Runner
from collections import deque

import numpy as np
import sched
import time

class PyAudioRunner(Runner):
    def __init__(self, chunk_size=256):
        super().__init__()

        self.chunk_size = chunk_size

    def run(self, generator):
        import pyaudio

        pa = pyaudio.PyAudio()

        generator = make_regular_generator(generator, self.chunk_size)
        target_frame_delta = self.chunk_size

        last_played_frame = 0
        last_generated_start = 0

        chunk_queue = deque()
        iterator = iter(generator)

        def callback(in_data, frame_count, time_info, status):
            nonlocal last_played_frame

            print('requested_frames', frame_count)
            print('last_played_frame', last_played_frame)
            print()
            last_played_frame += frame_count
            return (chunk_queue.popleft(), pyaudio.paContinue)


        def time_func():
            return last_played_frame


        def delay_func(frames):
            print('frames', frames)
            print('frame_rate', generator.frame_rate)
            delay = frames / generator.frame_rate
            print('delay', delay)
            print()
            time.sleep(delay)


        def fill_runner_queue():
            nonlocal last_played_frame
            nonlocal last_generated_start
            nonlocal chunk_queue

            if not stream.is_active():
                cancel_all_events(scheduler)
                return

            target_frame = last_played_frame + target_frame_delta

            while last_generated_start <= target_frame:
                chunk = np.copy(next(iterator))
                channels, frame_count = chunk.shape
                chunk_queue.append(chunk)

                last_generated_start += frame_count

            scheduler.enterabs(target_frame, 1, fill_runner_queue)


        #TODO: Initialize other parameters from generator.
        # Multiple channels might be nice

        stream = pa.open(
            format = pyaudio.paFloat32,
            channels = 1,
            rate = generator.frame_rate,
            stream_callback = callback,
            output = True,
            frames_per_buffer=self.chunk_size,
        )

        scheduler = sched.scheduler(time_func, delay_func)

        # Ready
        chunk = np.copy(next(iterator))

        # Set
        chunk_queue.append(chunk)

        # Go
        scheduler.enter(0, 1, fill_runner_queue)

        stream.start_stream()
        scheduler.run()
        stream.stop_stream()
        stream.close()

        pa.terminate()


def cancel_all_events(scheduler):
    events = list(scheduler.queue)
    for e in events:
        scheduler.cancel(e)
