import sys
import yaml as yml

def yaml(i, y, quiet=False):
    if quiet:
        return
    opts = {
        'default_flow_style': False,
        'allow_unicode': True,
    }
    safe = yml.safe_dump({i:y}, **opts)
    sys.stdout.write(safe+'\n')
    sys.stdout.flush()
