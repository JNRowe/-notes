#! /usr/bin/python3

import json
import re

import jinja2


with open('data/abbrevs.dat') as f:
    ABBREVS = [l.strip() for l in f]
_ABBRREVISE = lambda s: ''.join([s[0] for s in s.split()])  # NOQA
ABBREVS = {re.compile(fr'\b{_ABBRREVISE(s)}\b'):
           f'<abbr title="{s}">{_ABBRREVISE(s)}</abbr>'
           for s in ABBREVS}
ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
HTML_FILTERS = {
    re.compile(r'(#\w+)'): r'<b>\1</b>',
    re.compile(r'(https?://[\w\.?=\+/_-]+)', re.IGNORECASE):
        r'<a href="\1">\1</a>',
    re.compile(r'(@\w+(?:@\w+)*)'): r'<em>\1</em>',
}


def htmlise(dct):
    if 'text' in dct:
        for pat, repl in HTML_FILTERS.items():
            dct['text'] = pat.sub(repl, dct['text'])
        for pat, repl in ABBREVS.items():
            dct['text'] = pat.sub(repl, dct['text'])
    return dct


with open('data/notes.json') as f:
    notes = json.load(f, object_hook=htmlise)

tmpl = ENV.get_template('notes.jinja')

print(tmpl.render(notes=notes))
