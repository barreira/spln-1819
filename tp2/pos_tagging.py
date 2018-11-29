# coding=utf-8
import os
import re
import pandas as pd
import spacy
from spacy import displacy
from spacy.util import update_exc
from pathlib import Path
from prettytable import PrettyTable
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt

''' Implementation of spaCy's functionality

Collection of functions that implement some of spaCy's functionality: part-of-speech (POS) tagging, entity recognition,
information about tokens, dependency visualization and token exceptions.

These functions support both the web app as well as the terminal client.
'''

# Gerar tabelas (auxiliares)
def generate_html_table(headers, data):
    res = '<table class="table table-striped">\n'
    res += '  <thead><tr><th>' + '    </th><th>'.join(headers) + '  </th></tr></thead>\n  <tbody>\n'
    for sublist in data:
        res += '  <tr><td>'
        res += '    </td><td>'.join(sublist)
        res += '  </td></tr>\n'
    res += '  </tbody>\n</table>\n'
    return res

def generate_table(headers, data):
    table = PrettyTable()
    table.field_names = headers
    for row in data:
        table.add_row(row)
    return table

# Part-of-speech tagging
def generate_pos_chart(doc, filename='pos_frequence.svg', type='html'):
    tag_dict = {w.pos : w.pos_ for w in doc}
    pos_freq = []
    pos_tags = []
    for pos_id, freq in doc.count_by(spacy.attrs.POS).items():
        pos_freq.append(freq / len(doc))
        pos_tags.append(tag_dict[pos_id])
    if type=='html':
        return [['POS Tag', 'POS Frequence (%)']] + [list(x) for x in zip(pos_tags,pos_freq)]
    else:
        plt.barh(range(1,len(pos_tags)+1), pos_freq, tick_label=pos_tags)
        plt.savefig(filename)

# Get token's information
def generate_information(doc, vocab, type='html'):
    # python3 -m spacy download pt
    headers = ["Text","Lemma", "POS", "TAG", "DEP", "SHAPE", "MORPHOLOGIAL INFO", "IS_ALPHA", "IS_STOP"]
    data = []
    tokens = []

    for token in doc:
        if (str(token.pos_) != 'SPACE' and str(token.pos_) != 'PUNCT') or token.text not in tokens:
            if token.tag_:
                morph_info = dict(filter(lambda x : x[0]!=74, vocab.morphology.tag_map[token.tag_].items()))
                if not morph_info:
                    morph_info = ''
            else:
                morph_info = ''
            data.append([str(s) for s in (token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                    token.shape_, morph_info, token.is_alpha, token.is_stop)])
            tokens.append(token.text)

    if type=='html':
        return generate_html_table(headers, data)
    else:
        return generate_table(headers, data)


# Dependencies Graph
def generate_dependencies_graph(doc, type='service', compact = False, background='white',
                                            color='black', font='Source Sans Pro'):
    res = []
    if type in ('service', 'html', 'pict'):
        docs = list(doc.sents)
        options = {'compact': compact, 'bg': background, 'color': color, 'font': font}
    if type == 'service':
        displacy.serve(docs, style='dep', options=options)
    elif type == 'html':
        html = displacy.render(docs, style='dep', page=True, options=options)
        html = re.sub(r'.*<body[^>]*>(.*)</body>.*', r'\1', html, flags=re.DOTALL)
        res.append(html)
    elif type == 'pict':
        for doc in docs:
            pict = displacy.render(doc, style='dep', options=options)
            res.append(pict)
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
    else:
        res_list = []
        for word in doc:
            if word.ent_type_:
                res_list.append(str(word) + '{' + word.ent_type_ + '}')
            else:
                res_list.append(str(word))
        res = ' '.join(res_list)
    return res

# Rule-based morphology
def add_tokenizer_exceptions(nlp, tokens, tokenizer=None):
    if not tokenizer:
        tokenizer = nlp.tokenizer
    for token, token_attrs in tokens.items():
        tokenizer.add_special_case(token, token_attrs)

__author__ = "João Barreira, Mafalda Nunes"
__email__  = "a73831@alunos.uminho.pt, a77364@alunos.uminho.pt"
