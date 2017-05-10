from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = [ 'Runner' ]

class Runner(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    

    @abstractmethod
    def run(self, generator):
        pass
