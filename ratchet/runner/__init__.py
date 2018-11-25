'''
    Runners are clases which are responsible for consuming sample blocks from
    sound generator (see the generator package) and directing them to output
    for playback, file writing, etc.  See documentation for the runner module
    for further explanation.
'''

from .file_writer import FileWriter
from .pyaudio import PyAudioRunner
from .runner import Runner
