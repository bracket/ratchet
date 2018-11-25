'''
    Sound generators are classes providing functionality to generate and
    compose blocks of sound samples.  See documentation for the sound_generator
    module for further explanation of generators.
'''

from .generic import GenericGenerator
from .microphone import Microphone
from .sine import SineGenerator
from .sound_generator import SoundGenerator
from .wave_table import WaveTable
