from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = [ 'SoundGenerator' ]

class SoundGenerator(object):
    __metaclass__ = ABCMeta

    def __init__(self, frame_rate):
        self.frame_rate = frame_rate


    def start(self):
        g = iter(self)
        next(g)
        return g


    @abstractmethod
    def __iter__(self):
        pass
