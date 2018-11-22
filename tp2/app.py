from flask import Flask, request, url_for, redirect, render_template
import spacy
from pos_tagging import generate_tagged_text, generate_pos_information, generate_dependencies_graph

app = Flask(__name__)

tagged_text = ''
pos_info = ''
graphs = ''


@app.route('/', methods=['GET', 'POST'])
def index():
    global nlp, tagged_text, pos_info, graphs 
    if request.method == 'POST':
        nlp = spacy.load(request.values.get('lang'))
        doc = nlp(request.values.get('input'))
        tagged_text = generate_tagged_text(doc, type = 'html')
        pos_info = generate_pos_information(doc)
        graphs = '\n'.join(generate_dependencies_graph(doc, type = 'html'))
        return redirect(url_for('tagged_text_form'))
    return render_template('index.html')


@app.route('/tagged_text_form', methods=['GET', 'POST'])
def tagged_text_form():
    global tagged_text
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('tagged_text_form.html', tagged_text=tagged_text)


@app.route('/pos_info_form', methods=['GET', 'POST'])
def pos_info_form():
    global pos_info
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('pos_info_form.html', table=pos_info)


@app.route('/graphs_form', methods=['GET', 'POST'])
def graphs_form():
    global graphs
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('graphs_form.html', graphs=graphs)


if __name__ == '__main__':
    app.run()
