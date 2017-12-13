import os
import csv
import html
import json
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

def wget_search(url):
    obj = wget_json(url)
    return obj['search']

def get_tagline(search):
    return search.get('description')

def find_links(word_loop):
    """
    Arguments
    ----------
    word_loop: iter(str)
    """
    WIKI_LANG = "www.wikidata.org/w/api.php?format=json&formatversion=2&action=wbsearchentities&continue=0&language={l}&search={0}&type={t}&uselang={l}"
    verb_fmt = lambda x: WIKI_LANG.format(x, t='property', l='en')
    noun_fmt = lambda x: WIKI_LANG.format(x, t='item', l='en')

    # Try to get items or properties
    for word in word_loop:
        item_url = noun_fmt(word)
        items = wget_search(item_url)
        if not len(items):
            raise err.Tree('no item', 'word', word)
        # Get all descriptions for word
        w_taglines = map(get_tagline, items)
        w_with_tags = filter(None, w_taglines)
        log.yaml(word, list(w_with_tags))

    URL = "tools.wmflabs.org/wikidata-todo/tree.html?q=486972&rp=279"

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
