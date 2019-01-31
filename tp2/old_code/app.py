# coding=utf-8
import sys
import getopt
import json
from pos_tagging import *
from flask import Flask, request, url_for, redirect, render_template

''' Web app and terminal client to use spaCy's features

Either launches the web app (if no parameters are provided) or takes an input file and produces output to file or the
terminal. This output can be: a table with information about tokens, a bar chart with POS tag frequence, a text tagged
with entities or a dependency graph.

Multi-language support via the -l/--lang parameter.
'''

# Processar argumentos do comando
def processArgs():
    info_out = ''
    pos_chart_out = ''
    tagged_text_out = ''
    graphs_out = ''
    lang = 'pt'
    inputfile = ''

    error = 'USAGE:\tpython3 app.py [(-i <outputfile> | -p <outputfile> | -t <outputfile> | -g <outputfile>) [-l <language>] <inputfile>]\n\n' + \
            'OPTIONS:\n' + \
            '\t-l\tlanguage - \'pt\' (default) or \'en\'\n' + \
            '\t-i\treturns table with information about tokens to outputfile (or \'shell\')\n' + \
            '\t-p\tgenerates bar chart with POS tag frequence to outputfile\n' + \
            '\t-t\treturns tagged text to outputfile (or \'shell\')\n' + \
            '\t-g\tgenerates dependencies graphs to outputfile.svg\n' +\
            '* if no options are provided, a web server will be initialized, where the input will be inserted and the output presented.'

    # Processar opções/argumentos do comando utilizado
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"i:p:t:g:l:hv",["info=","pos-chart=", "tagged-text=", "graphs=", "lang=","help","version"])
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
    
    if info_out or pos_chart_out or tagged_text_out or graphs_out:
        if len(args) == 1:
            inputfile = args[0]
        else:
            print(error)
            sys.exit(2)
    elif len(args)>0:
        print(error)
        sys.exit(2)

    return info_out, pos_chart_out, tagged_text_out, graphs_out, lang, inputfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global lang, nlp, tagged_text, info, graphs, bar_chart
    if request.method == 'POST':
        lang = request.values.get('lang')
        entities = request.form.getlist('entity')
        token_exceptions = json.loads(request.values.get('tokenExceptions'))
        add_tokenizer_exceptions(nlp[lang], token_exceptions)
        doc = nlp[lang](request.values.get('input'))
        tagged_text = generate_tagged_text(doc, type = 'html', entities = entities)
        info = generate_information(doc, nlp[lang].vocab)
        bar_chart = generate_pos_chart(doc, None, type='html')
        graphs = '\n'.join(generate_dependencies_graph(doc, type = 'html'))
        return redirect(url_for('tagged_text_form'))
    return render_template('index.html', lang=lang)


@app.route('/tagged_text_form', methods=['GET', 'POST'])
def tagged_text_form():
    global tagged_text
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('tagged_text_form.html', tagged_text=tagged_text)


@app.route('/info_form', methods=['GET', 'POST'])
def info_form():
    global info, bar_chart
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('info_form.html', table=info, bar_chart=bar_chart)


@app.route('/graphs_form', methods=['GET', 'POST'])
def graphs_form():
    global graphs
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('graphs_form.html', graphs=graphs)


if __name__ == '__main__':
    global tagged_text, info, graphs
    info_out, pos_chart_out, tagged_text_out, graphs_out, lang, inputfile = processArgs()
    if inputfile:
        if lang == 'en':
            nlp = spacy.load('en_core_web_lg')
        else:
            nlp = spacy.load('pt')
        with open(inputfile, 'r') as input:
            doc = nlp(input.read())
        if info_out:
            output = generate_information(doc, nlp.vocab, 'text')
            if info_out == 'shell':
                print(output)
            else:
                with open(info_out, 'w') as fd:
                    fd.write(output)
        if pos_chart_out:
            generate_pos_chart(doc, pos_chart_out, type='pict')
        if tagged_text_out:
            output = generate_tagged_text(doc, 'text', nlp.vocab)
            if tagged_text_out == 'shell':
                print(output)
            else:
                with open(tagged_text_out, 'w') as fd:
                    fd.write(output)
        if graphs_out:
            os.makedirs('./images', exist_ok=True)
            pictures = generate_dependencies_graph(doc, 'pict')
            for i, pict in enumerate(pictures):
                file_name = graphs_out + '_' + str(i) + '.svg'
                output_path = Path('./images/' + file_name)
                with output_path.open('w', encoding='utf-8') as output_file:
                    output_file.write(pict)
    else:
        nlp = {'en': spacy.load('en_core_web_lg'), 'pt': spacy.load('pt') }
        tagged_text = ''
        info = ''
        graphs = ''
        app.run()

__author__ = "João Barreira, Mafalda Nunes"
__email__  = "a73831@alunos.uminho.pt, a77364@alunos.uminho.pt"