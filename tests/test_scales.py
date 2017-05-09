from pytest import approx
from ratchet.scales import Pitch, Duration, Note

def test_scales():
    from ratchet.scales import make_scale

    tests = {
        ('c', 'major') : [ 'c', 'd', 'e', 'f', 'g', 'a', 'b'  ],
        ('g', 'major') : [ 'g', 'a', 'b', 'c', 'd', 'e', 'f#' ],
    }

    for scale, expected in tests.items():
        actual = make_scale(*scale)
        actual = sorted(actual, key=actual.get)
        assert actual == expected


def test_frequency():
    from ratchet.scales import pitch_to_frequency

    tests = {
        Pitch('c', 4, '') : 261.625565,
        Pitch('a', 4, '') : 440.0,
    }

    for pitch, expected in tests.items():
        actual = pitch_to_frequency(pitch)
        assert actual == approx(expected)


def test_parse_notes():
    from ratchet.scales import parse_notes
    from ratchet.scales import Pitch, Note, Duration

    notes = 'c4/2 c4#/4 d2/2o a4bn/1'

    expected = [
        Note(
            Pitch('c', 4, None),
            Duration(2, None)
        ),
        Note(
            Pitch('c', 4, '#'),
            Duration(4, None)
        ),
        Note(
            Pitch('d', 2, None),
            Duration(2, 'o')
        ),
        Note(
            Pitch('a', 4, 'bn'),
            Duration(1, None)
        )
    ]

    for e, a in zip(expected, parse_notes(notes)):
        assert a == e
