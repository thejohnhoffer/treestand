import sys

from . import log

class Tree(ValueError):
    pass

def wrap(cmd, main, *args):
    argv = sys.argv[1:]
    try:
        parsed = cmd.parse_args(argv)
        main(parsed, *args)
        print('Done')
    except Tree as e:
        err, key, val = e.args
        log.yaml('Tree Error', [
            {
                key: val,
            },
            err,
        ])
