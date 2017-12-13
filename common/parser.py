import argparse

flags = {
    'words': ['-w','--words'],
}

def key(k):
    helps = {
        'words': '/path/to/words.csv (default {})',
    }
    defaults = {
        'words': 'data/1000.csv',
    }
    choices = {
    }
    keys = {
        'help': helps.get(k, '???'),
    }
    if k in defaults:
        v = defaults[k]
        keys['default'] = v
        keys['type'] = type(v)
        keys['help'] = keys['help'].format(v)
    if k in choices:
        keys['choices'] = choices[k]

    return keys

def add_argument(cmd, i):

    words = flags.get(i,[i])
    cmd.add_argument(*words, **key(i))

def setup(_filename, _describe, _items=[]):
    COMMAND = _filename
    DETAILS = _describe + '\n'
    ' We use Wikidata to relate concepts.'

    # Parse with defaults
    cmd = argparse.ArgumentParser(**{
        'prog': COMMAND,
        'description': DETAILS,
        'formatter_class': argparse.RawTextHelpFormatter,
    })

    positional = []
    optional = [
	'words'
    ]
    items = positional + optional
    # Allow custom items
    if _items:
        items = _items
    for i in items:
        add_argument(cmd, i)

    return cmd
