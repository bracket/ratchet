from collections import namedtuple

__all__ = [ 'Interval' ]

Interval_ = namedtuple('Interval_', [ 'start', 'end' ])

class Interval(Interval_):
    def length(self):
        return self.end - self.start


    def intersection(self, other):
        return Interval(max(self.start, other.start), min(self.end, other.end))


    def shift(self, amount):
        return Interval(self.start + amount, self.end + amount)


    def slice(self):
        return slice(self.start, self.end)


    def __sub__(self, right):
        return Interval(self.start - right


    def __repr__(self):
        return 'Interval({}, {})'.format(self.start, self.end)
