import yaml as yml

def yaml(i, y, quiet=False):
    if quiet:
        return
    opts = {
        'default_flow_style': False,
    }
    safe = yml.safe_dump({i:y}, **opts)
    print(safe)
