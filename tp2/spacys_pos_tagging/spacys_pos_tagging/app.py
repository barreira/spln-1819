# coding=utf-8
#!/usr/bin/python3

''' Web app and terminal client to use spaCy's features

Either launches the web app (if no parameters are provided) or takes an input file and produces
output to file or the terminal. This output can be: a table with information about tokens, a bar
chart with POS tag frequence, a text tagged with entities or a dependency graph.

Multi-language support via the -l/--lang parameter.
'''

import os
import sys
import getopt
from pathlib import Path
import json
import spacy
from flask import Flask, request, url_for, redirect, render_template
from .pos_tagging import add_tokenizer_exceptions, generate_tagged_text, generate_information, \
generate_pos_chart, generate_dependencies_graph

APP = Flask(__name__)

@APP.route('/', methods=['GET', 'POST'])
def index():
    '''
    On 'GET' displays index template.
    On 'POST' colect all necessary input and redirect to the next form.
    '''
    if request.method == 'POST':
        APP.config['LANG'] = request.values.get('lang')
        entities = request.form.getlist('entity')
        token_exceptions = json.loads(request.values.get('tokenExceptions'))
        add_tokenizer_exceptions(APP.config['NLP'][APP.config['LANG']], token_exceptions)
        doc = APP.config['NLP'][APP.config['LANG']](request.values.get('input'))
        APP.config['TAGGED_TEXT'] = generate_tagged_text(doc, style='html', entities=entities)
        APP.config['INFO'] = generate_information(doc, APP.config['NLP'][APP.config['LANG']].vocab)
        APP.config['BAR_CHART'] = generate_pos_chart(doc, None, style='html')
        APP.config['GRAPHS'] = '\n'.join(generate_dependencies_graph(doc, style='html'))
        return redirect(url_for('tagged_text_form'))
    return render_template('index.html', lang=APP.config['LANG'])


@APP.route('/tagged_text_form', methods=['GET', 'POST'])
def tagged_text_form():
    '''
    On 'GET' displays tagged_text_form template.
    On 'POST' redirect to index form.
    '''
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('tagged_text_form.html', tagged_text=APP.config['TAGGED_TEXT'])


@APP.route('/info_form', methods=['GET', 'POST'])
def info_form():
    '''
    On 'GET' displays info_form template.
    On 'POST' redirect to index form.
    '''
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('info_form.html', table=APP.config['INFO'],
                           bar_chart=APP.config['BAR_CHART'])


@APP.route('/graphs_form', methods=['GET', 'POST'])
def graphs_form():
    '''
    On 'GET' displays graphs_form template.
    On 'POST' redirect to index form.
    '''
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('graphs_form.html', graphs=APP.config['GRAPHS'])


def spacys_features(arguments):
    '''
    Provides spacy's features on command line and web interface.
    '''
    info_out, pos_chart_out, tagged_text_out, graphs_out, lang, inputfile = arguments
    if inputfile:
        nlp = {'en': 'en_core_web_lg', 'pt': 'pt'}
        nlp = spacy.load(nlp[lang])
        with open(inputfile, 'r') as inp:
            doc = nlp(inp.read())
        if info_out:
            output = generate_information(doc, nlp.vocab, 'text')
            if info_out == 'shell':
                print(output)
            else:
                with open(info_out, 'w') as file_descriptor:
                    file_descriptor.write(output)
        if pos_chart_out:
            generate_pos_chart(doc, pos_chart_out, style='pict')
        if tagged_text_out:
            output = generate_tagged_text(doc, 'text', nlp.vocab)
            if tagged_text_out == 'shell':
                print(output)
            else:
                with open(tagged_text_out, 'w') as file_descriptor:
                    file_descriptor.write(output)
        if graphs_out:
            os.makedirs('./images', exist_ok=True)
            output = generate_dependencies_graph(doc, 'pict')
            for i, pict in enumerate(output):
                output_path = Path('./images/' + graphs_out + '_' + str(i) + '.svg')
                with output_path.open('w', encoding='utf-8') as file_descriptor:
                    file_descriptor.write(pict)
    else:
        APP.config['NLP'] = {'en': spacy.load('en_core_web_lg'), 'pt': spacy.load('pt')}
        APP.config['LANG'] = 'pt'
        APP.config['TAGGED_TEXT'] = ''
        APP.config['INFO'] = ''
        APP.config['GRAPHS'] = ''
        APP.config['BAR_CHART'] = None
        APP.run()

# Processar argumentos do comando
def process_args():
    '''
    Proccess arguments from command line.
    '''
    info_out = ''
    pos_chart_out = ''
    tagged_text_out = ''
    graphs_out = ''
    lang = 'pt'
    inputfile = ''

    error = 'USAGE:\tspacys_features app.py [(-i <outputfile> | -p <outputfile> | -t <outputfile> | ' + \
            '-g <outputfile>) [-l <language>] <inputfile>]\n\n' + \
            'OPTIONS:\n' + \
            '\t-l\tlanguage - \'pt\' (default) or \'en\'\n' + \
            '\t-i\treturns table with information about tokens to outputfile (or \'shell\')\n' + \
            '\t-p\tgenerates bar chart with POS tag frequence to outputfile\n' + \
            '\t-t\treturns tagged text to outputfile (or \'shell\')\n' + \
            '\t-g\tgenerates dependencies graphs to outputfile.svg\n' +\
            '* if no options are provided, a web server will be initialized, where the input ' + \
            'will be inserted and the output presented.'

    # Processar opções/argumentos do comando utilizado
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:p:t:g:l:hv",
                                   ["info=", "pos-chart=", "tagged-text=", "graphs=", "lang=",
                                    "help", "version"]
                                   )
    except getopt.GetoptError:
        print(error)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(error)
            sys.exit()
        elif opt in ('-v', '--version'):
            print('Version 1.0')
            sys.exit()
        elif opt in ("-i", "--info"):
            info_out = arg
        elif opt in ("-p", "--pos-chart"):
            pos_chart_out = arg
        elif opt in ("-t", "--tagged-text"):
            tagged_text_out = arg
        elif opt in ("-g", "--graphs"):
            graphs_out = arg
        elif opt in ("-l", "--lang"):
            lang = arg

    if (info_out or pos_chart_out or tagged_text_out or graphs_out) and len(args) == 1:
        inputfile = args[0]
    elif info_out or pos_chart_out or tagged_text_out or graphs_out or args:
        print(error)
        sys.exit(2)

    spacys_features((info_out, pos_chart_out, tagged_text_out, graphs_out, lang, inputfile))


__author__ = "João Barreira, Mafalda Nunes"
__email__ = "a73831@alunos.uminho.pt, a77364@alunos.uminho.pt"
