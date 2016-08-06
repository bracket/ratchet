from collections import namedtuple

major_steps = [ 2, 2, 1, 2, 2, 2, 1 ]
major_scale = [ sum(major_steps[:i]) for i in range(len(major_steps)) ]

c_major = dict(zip('cdefgab', major_scale))

middle_major_octave = { c : 440. * pow(2., (i - c_major['a'])/12.) for c, i in c_major.items() }

def make_note_grammar():
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


note_grammar = make_note_grammar()


def tokenize(regex, text):
    start, end = 0, len(text)

    while start < end:
        match = regex.match(text, start)
        yield match
        start = match.end()


def parse_notes(text):
    for match in tokenize(note_grammar['token'], text):
        if match.group('ws'): continue

        yield match


Pitch = namedtuple('Pitch', 'name octave accents')
Duration = namedtuple('Duration', 'length length_modifier')
Note = namedtuple('Note', 'pitch duration')
