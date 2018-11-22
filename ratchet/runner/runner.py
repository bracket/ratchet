from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = [ 'Runner' ]

class Runner(object):
    '''
        Base class for all runners.  Derived classes must implement the run
        method, which consumes blocks from the attached generator and writes it
        to some output device.
    '''
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, generator):
        pass
