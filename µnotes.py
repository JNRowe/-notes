#! /usr/bin/python3

import html
import json
import re

from xml.sax.saxutils import quoteattr

import jinja2

from ciso8601 import parse_datetime
from jnrbase.attrdict import AttrDict


def tag(name, attribs=None, text=r'\1'):
    if attribs:
        attribs = ' ' + ' '.join(f'{k}={quoteattr(v)}'
                                 for k, v in attribs.items())
    else:
        attribs = ''
    res = f'\N{STX}{name}{attribs}\N{ETX}'
    if text:
        res += f'{text}\N{STX}/{name}\N{ETX}'
    return res


with open('data/abbrevs.dat') as f:
    ABBREVS = [l.strip() for l in f]
_ABBRREVISE = lambda s: ''.join([s[0] for s in s.split()])  # NOQA
ABBREVS = {re.compile(fr'\b{_ABBRREVISE(s)}\b'):
           tag('abbr', {'title': html.escape(s, True)}, _ABBRREVISE(s))
           for s in ABBREVS}
ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
HTML_FILTERS = {
    re.compile(r'(?<!&)(#[a-zA-Z_]\w+(?=[^\d\S]|\W))', re.IGNORECASE):
        tag('b'),
    re.compile(r'(https?://[\w\.?=\+/_-]+)', re.IGNORECASE):
        tag('a', {'href': r'\1'}),
    re.compile(r'\B(@\w+(?:@\w+)*)'): tag('em'),
    re.compile(r'\B/(\w+)/\B'): tag('em'),
    re.compile(r'\*(\w+)\*'): tag('strong'),
    re.compile(r'``(.*?)``'): tag('code'),
    re.compile(r'\n'): tag('br', text=None),
}


def munge(dct):
    dct = AttrDict(**dct)
    if 'text' in dct:
        dct.text = html.escape(dct.text)
        for pat, repl in HTML_FILTERS.items():
            dct.text = pat.sub(repl, dct.text)
        for pat, repl in ABBREVS.items():
            dct.text = pat.sub(repl, dct.text)
        dct.text = dct.text.replace('\N{STX}', '<').replace('\N{ETX}', '>')
    if 'timestamp' in dct:
        dct.timestamp = parse_datetime(dct.timestamp)
    if 'self' in dct:
        dct.self = parse_datetime(dct.self)
    return dct


with open('data/notes.json') as f:
    notes = json.load(f, object_hook=munge)

with open('data/config.json') as f:
    config = json.load(f, object_hook=AttrDict)

tmpl = ENV.get_template('notes.jinja')

print(tmpl.render(notes=notes, **config))
