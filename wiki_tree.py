import os
import sys
import csv
import html
import json
import urllib
import http.client
from common import log
from common import err
from common import parser

def wget(url):
    """
    Arguments
    ----------
    url: str
    """
    url_parts = url.split('/')
    url_host = url_parts.pop(0)
    url_path = '/'+'/'.join(url_parts)
    conn = http.client.HTTPSConnection(url_host)
    conn.request("GET", url_path)
    r = conn.getresponse()
    if r.status != 200:
        msg = 'HTTP {}'.format(r.status)
        raise err.Tree(msg, 'URL', url)
    # Return full data
    output = r.read()
    conn.close()
    return output

def wget_json(url):
    text = wget(url)
    return json.loads(text)

def wget_key(url, key):
    obj = wget_json(url)
    return obj.get(key)

def filter_all(results, *keys):
    """ Get results that have certain keys
    """
    if_all = lambda r: all(map(r.get, keys))
    with_all = filter(if_all, results)
    # Sort by shortest values of first property
    sort_prop = lambda a: len(a[keys[0]])
    return sorted(with_all, key=sort_prop)

def filter_label(results, no=None):
    """ Get results that match label (not alias)
    """
    get_type = lambda r: r.get('match',{}).get('type')
    is_label = lambda r: get_type(r) == 'label'
    out = filter(is_label, results)
    # Further refine if given blacklist
    if not no:
        return list(out)
    no_no = lambda o: no not in o.get('label', no)
    return list(filter(no_no, out))

def get_keys(*keys):
    if len(keys) == 1:
        return lambda r: next(map(r.get,keys),'')
    return lambda r: list(map(r.get, keys))

def find_links(word_loop):
    """
    Arguments
    ----------
    word_loop: iter(str)
    """
    def fmt_fwd(p,q):
        return ' '.join([
        'SELECT ?item ?V WHERE {',
        'VALUES ?roots {wd:Q%s}  .' % q,
        '?tree (wdt:p{})* ?item'.format(p),
        'OPTIONAL {',
        '?item wdt:P{} ?V'.format(p),
        '} }'])
    def fmt_rev(p,q):
        return ' '.join([
        'SELECT ?item ?V WHERE {',
        'VALUES ?roots {wd:Q%s}  .' % q,
        '?item (wdt:P{})* ?roots'.format(p),
        'OPTIONAL {',
        '?item wdt:P{} ?V'.format(p),
        '} }'])

    WIKI_BASE = "query.wikidata.org/sparql?{}"
    WIKI_ID = "www.wikidata.org/w/api.php?format=json&formatversion=2&action=wbsearchentities&continue=0&language={l}&search={0}&type={t}&uselang={l}"
    WIKI_NAME = "www.wikidata.org/w/api.php?format=json&action=wbgetentities&props=labels&ids={t}{0}&languages={l}"
    rev_verb_fmt = lambda x: WIKI_NAME.format(x, t='P', l='en')
    rev_noun_fmt = lambda x: WIKI_NAME.format(x, t='Q', l='en')
    verb_fmt = lambda x: WIKI_ID.format(x, t='property', l='en')
    noun_fmt = lambda x: WIKI_ID.format(x, t='item', l='en')

    # Try to get items or properties
    for word in word_loop:
        props = wget_key(verb_fmt(word),'search')
        items = wget_key(noun_fmt(word),'search')
        if not len(items):
            log.yaml('ERR, No item', word)
            #raise err.Tree('no item', 'word', word)
        # Filter for matching labels (no spaces)
        label_props = filter_all(props,'label','description')
        label_items = filter_all(items,'label','description')
        ok_props = filter_label(label_props, no=' ')
        ok_items = filter_label(label_items, no=' ')

        # Get queries and properties
        get_ld = get_keys('label', 'description')
        word_log = {
            'verb': list(map(get_ld, ok_props)),
            'noun': list(map(get_ld, ok_items)),
        }
        word_log = {
            k: v for k, v in word_log.items() if len(v)
        }
        get_label = lambda x: x.get('labels', {}).get('en', {}).get('value')
        # Make tree request:
        if 'noun' in word_log:
            ok_i = next(iter(ok_items), None)
            if not ok_i:
                log.yaml('ERR {}'.format(word), 'No item matches')
                break
            ok_title = ''.join(i for i in ok_i['title'] if i.isdigit())
            tree_ql = fmt_rev(31, ok_title)
            tree_param = urllib.parse.urlencode({
                'query': tree_ql,
                'format': 'json',
            })
            tree_url = WIKI_BASE.format(tree_param)
            res_key = ' '.join(get_ld(ok_i))
            res = wget_key(tree_url,'results')
            short_res = []
            for r in res.get('bindings',[]):
                v_raw = r.get('V', {}).get('value',None)
                if not v_raw:
                    short_res.append('?')
                    continue
                # Get the short name of the result
                v_id = v_raw.split('/')[-1]
                v_url = rev_noun_fmt(v_id[1:])
                v_search = wget_key(v_url, 'entities')
                v_vals = v_search.values()
                v_en = filter(None,map(get_label, v_vals))
                short_res.append(next(v_en, None))
            log.yaml(res_key, short_res)

    URL = "tools.wmflabs.org/wikidata-todo/tree.html"
    UI = "https://angryloki.github.io/wikidata-graph-builder"

def open_words(word_path):
    with open(word_path,'r') as wf:
        for w in csv.reader(wf):
            yield next(iter(w),'')

def main(arg):
    try:
        word_loop = open_words(arg.words)
    except OSError as e:
        raise err.Tree(str(e), 'word path', word_path)
    # Make request to Wikidata
    find_links(word_loop)

if __name__ == "__main__":

    filename = os.path.basename(__file__)
    describe = 'Get links between words.'
    cmd = parser.setup(filename, describe)
    # Handle exceptions
    err.wrap(cmd, main)
