from collections import namedtuple

import os
import subprocess as sp
import numpy as np

__all__ = [ 'Delay', 'Marker', 'Voice', 'Script' ]

Delay = namedtuple('Delay', 'milliseconds')
Jump = namedtuple('Jump', 'name')
Marker = namedtuple('Marker', 'name')
Silence = namedtuple('Silence', 'milliseconds')
Voice = namedtuple('Voice', 'voice phrase')


class Script(object):
    def __init__(self, items, framerate=None, nchannels=None):
        self.items = items

        self.framerate = 22050 if framerate is None else framerate
        self.nchannels = 1 if nchannels is None else nchannels

        self.currentvoice = 'Daniel'


    def render(self):
        out = np.array([], np.int16)
        current_offset = 0
        markers = { }

        for item in self.items:
            if isinstance(item, (int, float)):
                delay = Delay(item)
                current_offset = self.render_delay(out, current_offset, delay)
            elif isinstance(item, str):
                voice = Voice(self.currentvoice, item)
                current_offset = self.render_voice(out, current_offset, voice)
            elif isinstance(item, Voice):
                current_offset = self.render_voice(out, current_offset, item)
            elif isinstance(item, Delay):
                current_offset = self.render_delay(out, current_offset, item)
            elif isinstance(item, Marker):
                if item in markers:
                    markers[item].append(current_offset)
                else:
                    markers[item] = [ current_offset ]
            else:
                raise RuntimeError('unidentified item in ratchet script')

        return out[:current_offset], markers


    def render_delay(self, out, current_offset, delay):
        offset = int((delay.milliseconds / 1e3) * self.framerate)
        end_offset = current_offset + offset

        if end_offset < current_offset:
            out[end_offset:current_offset] = 0
        elif end_offset > len(out):
            out.resize(end_offset, refcheck=False)
            out[current_offset:end_offset] = 0

        return end_offset


    def render_voice(self, out, current_offset, voice):
        import aifc
        from tempfile import TemporaryDirectory

        self.currentvoice = voice.voice

        with TemporaryDirectory() as directory:
            path = os.path.join(directory, 'voice.caff')
            
            command = [
                'say',
                '-v', voice.voice,
                '-o', path,
                voice.phrase
            ]

            sp.check_call(command)

            with aifc.open(path, 'rb') as pcm:
                nframes = pcm.getnframes()

                data = pcm.readframes(nframes)
                data = np.frombuffer(data, dtype=np.int16)

                if len(out) < current_offset + len(data):
                    out.resize(current_offset + len(data), refcheck=False)

                out[current_offset:current_offset + len(data)] = data

                return current_offset + len(data)
