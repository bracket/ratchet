from collections import namedtuple

from .util import memoize

@memoize
def scale_steps(scale):
    steps = {
        'major'          : [ 2, 2, 1, 2, 2, 2, 1 ],
        'minor_natural'  : [ 2, 1, 2, 2, 1, 2, 2 ],
        'minor_harmonic' : [ 2, 1, 2, 2, 1, 3, 1 ],
        'minor_melodic'  : [ 2, 1, 2, 2, 2, 2, 1 ],
        'chromatic'      : [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
    }

    return steps[scale]


@memoize
def scale_offsets(scale):
    steps = scale_steps(scale)
    return [ sum(steps[:i]) for i in range(len(steps)) ]


notes_sharp = [ 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b' ]
notes_flat =  [ 'c', 'db', 'd', 'eb', 'e', 'f', 'gb', 'g', 'ab', 'a', 'bb', 'b' ]


def make_chromatic_scale(tonic):
    for notes in (notes_sharp, notes_flat):
        try:
            i = notes.index(tonic)
            return notes[i:] + notes[:i]
        except ValueError:
            pass


@memoize
def make_scale(tonic, scale):
    offsets = dict(zip(scale_offsets('chromatic'), make_chromatic_scale(tonic)))
    return { offsets[o] : o for o in scale_offsets(scale) }


def pitch_to_frequency(pitch, a4=440.):
    from math import pow

    a4_step = 12 * 4 + 9
    chromatic = make_scale('c', 'chromatic')

    sharps, flats = parse_accents(pitch.accents)

    steps = 12 * pitch.octave + chromatic[pitch.name] + sharps - flats
    steps -= a4_step

    return a4 * pow(2., steps/12.)


def pitch_to_midi(pitch):
    a4_step = 12 * 4 + 9
    chromatic = make_scale('c', 'chromatic')

    sharps, flats = parse_accents(pitch.accents)

    steps = 12 * pitch.octave + chromatic[pitch.name] + sharps - flats
    steps -= a4_step

    return 69 + steps


def parse_accents(accents):
    sharps, flats = 0, 0

    for a in accents:
        if a == '#':
            if flats:
                flats -= 1
            else:
                sharps += 1
        elif a == 'b':
            if sharps:
                sharps -= 1
            else:
                flats += 1
        elif a == 'n':
            sharps, flats = 0, 0

    return (sharps, flats)


@memoize
def note_grammar():
    import re

    g = { }

    g['name']     = r'[a-gA-G]'
    g['sign']     = r'[-+]'
    g['digits']   = r'[0-9]+'
    g['integer']  = r'{sign}?{digits}'.format(**g)
    g['accents']  = r'[#bn]+'

    g['pitch']    = r'(?P<name>{name})(?P<octave>{integer})(?P<accents>{accents})?'.format(**g)
    g['duration'] = r'/(?P<length>{digits})(?P<length_modifier>o)?'.format(**g)

    g['note']     = r'{pitch}{duration}'.format(**g)
    g['ws']       = r'(?:\s+)'

    tokens = [ 'ws', 'note' ]
    g['token'] = '|'.join('(?P<{}>{})'.format(name, g[name]) for name in tokens)

    for key, value in g.items():
        g[key] = re.compile(value)

    return g


def tokenize(regex, text):
    start, end = 0, len(text)

    while start < end:
        match = regex.match(text, start)

        if not match:
            raise TokenizationError('no match', { 'text' : text, 'start' : start })

        if match.end() == start:
            raise TokenizationError('empty match', { 'text' : text, 'start' : start })

        yield match
        start = match.end()


class TokenizationError(Exception):
    pass


def parse_notes(text):
    token_re = note_grammar()['token']


    for match in tokenize(token_re, text):
        g  = match.group

        if g('ws'):
            continue

        pitch = Pitch(g('name'), int(g('octave')), g('accents'))
        duration = Duration(int(g('length')), g('length_modifier'))

        yield Note(pitch, duration)


Pitch = namedtuple('Pitch', 'name octave accents')
Duration = namedtuple('Duration', 'length length_modifier')
Note = namedtuple('Note', 'pitch duration')
