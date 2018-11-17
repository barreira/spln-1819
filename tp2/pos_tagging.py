import os
import re
import spacy
from spacy import displacy
from spacy.util import update_exc
from pathlib import Path

# https://spacy.io/usage/linguistic-features

def generate_html_table(headers, data):
    res = '<table class="table table-striped">\n'
    res += '  <thead><tr><th>' + '    </th><th>'.join(headers) + '  </th></tr></thead>\n  <tbody>\n'
    for sublist in data:
        res += '  <tr><td>'
        res += '    </td><td>'.join(sublist)
        res += '  </td></tr>\n'
    res += '  </tbody>\n</table>\n'
    return res

# Part-of-speech tagging
def generate_pos_information(doc):
    # python3 -m spacy download pt
    headers = ["Text","Lemma", "POS", "TAG", "DEP", "SHAPE", "IS_ALPHA", "IS_STOP"]
    data = []

    for token in doc:
        data.append([str(s) for s in (token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                token.shape_, token.is_alpha, token.is_stop)])
    
    return generate_html_table(headers, data)


# Dependencies Graph
def generate_dependencies_graph(doc, type='service', compact = False, background='white', 
                                            color='black', font='Source Sans Pro'):
    res = []
    if type in ('service', 'html', 'svg'):
        docs = list(doc.sents)
        options = {'compact': compact, 'bg': background, 'color': color, 'font': font}
    if type == 'service':
        displacy.serve(docs, style='dep', options=options)
    elif type == 'html':
        html = displacy.render(docs, style='dep', page=True, options=options)
        html = re.sub(r'.*<body[^>]*>(.*)</body>.*', r'\1', html, flags=re.DOTALL)
        res.append(html)
    elif type == 'svg':
        for doc in docs:
            svg = displacy.render(doc, style='dep', options=options)
            res.append(svg)
    return res


# Visualizing the entity recognizer
def generate_tagged_text(doc, type = 'server', entities = None, colors = None):
    res = ''
    if type in ('server', 'html'):
        options = {}
        if entities:
            options['ents'] = entities
        if colors:
            options['colors'] = colors
        if type=='server':
            displacy.serve(doc, style='ent', options=options)
        else:
            res = displacy.render(doc, style='ent', options=options)
    return res

# Rule-based morphology
