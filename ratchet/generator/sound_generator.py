from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = [ 'SoundGenerator' ]

class SoundGenerator(object):
    '''
        Base class for all sound generators.  Derived classes must implement
        __iter__, which produces blocks of PCM sound samples (as numpy arrays)
        on request, at the frame_rate requested in the base class.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, frame_rate):
        self.frame_rate = frame_rate


    @abstractmethod
    def __iter__(self):
        pass
