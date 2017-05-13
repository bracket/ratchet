from ..generator.regular import make_regular_generator
from .runner import Runner
import numpy as np
import sched
import time

class PyAudioRunner(Runner):
    def run(self, generator):
        import pyaudio

        pa = pyaudio.PyAudio()

        generator = make_regular_generator(generator, 1024)
        target_frame_delta = int(.1 * generator.frame_rate)
        generator.prime_queue(target_frame_delta)

        current_frame = 0
        iterator = generator.start()

        def callback(in_data, frame_count, time_info, status):
            nonlocal current_frame

            current_frame += frame_count
            return (iterator.send(frame_count), pyaudio.paContinue)


        def time_func():
            return current_frame


        def delay_func(frames):
            delay = frames / generator.frame_rate
            time.sleep(delay)


        def fill_generator_queue():
            if not stream.is_active():
                cancel_all_events(scheduler)
                return

            target_frame = current_frame + target_frame_delta

            while generator.last_start < target_frame:
                generator.extend_queue()

            scheduler.enterabs(target_frame, 1, fill_generator_queue)


        stream = pa.open(
            format = pyaudio.paFloat32,
            channels = 1,
            rate = generator.frame_rate,
            stream_callback = callback,
            output = True,
        )

        scheduler = sched.scheduler(time_func, delay_func)

        scheduler.enter(0, 1, fill_generator_queue)

        stream.start_stream()
        scheduler.run()
        stream.stop_stream()
        stream.close()

        pa.terminate()


def cancel_all_events(scheduler):
    events = list(scheduler.queue)
    for e in events:
        scheduler.cancel(e)
