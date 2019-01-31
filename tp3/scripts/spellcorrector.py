# coding=utf-8
#!/usr/bin/python3

''' Spell corrector with several operation modes

Corrects the input text according to default mode or indicated (aspell/hunspell/symspell).
Indicates also the load and correction time.
'''

import os
import sys
import time
import json
import getopt
import bisect
import fileinput
from collections import Counter, defaultdict

import spacy
import regex
from symspellpy.symspellpy import SymSpell, Verbosity
import aspell
import hunspell


####################           MODO MANUAL           ####################

def get_tag(token):
    "Tag of `token` (word or punctuation)"
    tags = list(filter(lambda x: x[0] != '<' and x[-1] != '>' and x[0] != '@', \
                        token.tag_.split('|')))
    if token.pos_ == 'ADV':
        token_str = str(token)
        if token_str == 'agora' or token_str == 'hoje':
            tags += '|Present'
        elif token_str == 'anteontem' or token_str == 'antes' or token_str == 'ontem' \
             or token_str == 'outrora':
            tags += '|Past'
        elif token_str == 'amanhã' or token_str == 'breve':
            tags += '|Future'
    return '<' + '|'.join(tags) + '>'


def get_pos_context(before_word, word, after_word, words_freq, nlp):
    "POS and tag context of `word`"
    if before_word and after_word:
        doc = nlp(before_word + ' ' + word + ' ' + after_word)
        pos_0 = '<UNKNOWN>' if before_word not in words_freq else doc[0].pos_ + get_tag(doc[0])
        pos_1 = '<UNKNOWN>' if word not in words_freq else doc[1].pos_ + get_tag(doc[1])
        pos_2 = '<UNKNOWN>' if after_word not in words_freq else doc[2].pos_ + get_tag(doc[2])
        context_pos = pos_0 + ' ' + pos_1 + ' ' + pos_2
    elif not before_word and after_word:
        doc = nlp(word + ' ' + after_word)
        pos_1 = '<UNKNOWN>' if word not in words_freq else doc[0].pos_ + get_tag(doc[0])
        pos_2 = '<UNKNOWN>' if after_word not in words_freq else doc[1].pos_ + get_tag(doc[1])
        context_pos = '__BEGIN__ ' + pos_1 + ' ' + pos_2
    elif before_word and not after_word:
        doc = nlp(before_word + ' ' + word)
        pos_0 = '<UNKNOWN>' if before_word not in words_freq else doc[0].pos_ + get_tag(doc[0])
        pos_1 = '<UNKNOWN>' if word not in words_freq else doc[1].pos_ + get_tag(doc[1])
        context_pos = pos_0 + ' ' + pos_1 + ' __END__'
    else:
        doc = nlp(word)
        pos_1 = '<UNKNOWN>' if word not in words_freq else doc[0].pos_ + get_tag(doc[0])
        context_pos = '__BEGIN__ ' + pos_1 + ' ' + '__END__'
    return context_pos


def probability(word, original_word, words_freq, pos_freqs, n_words, before_word, after_word, nlp):
    "Probability of `word`."
    context_pos = get_pos_context(before_word, word, after_word, words_freq, nlp)
    if word in words_freq:
        freq = (words_freq[word.lower()][word] / n_words) * \
                (60 if word.lower() != original_word.lower() else 100)
    else:
        freq = 0
    if context_pos:
        pos_freq = (99 * pos_freqs.get(context_pos, 0) + 1) / sum(pos_freqs.values())
        freq = freq * pos_freq * 100
    return freq


def correction(word, words_freq, pos_freqs, n_words, before_word, after_word, nlp):
    "Most probable spelling correction for word."
    return max(candidates(word, words_freq), key=lambda x: \
               probability(x, word, words_freq, pos_freqs, n_words, before_word, after_word, nlp))

def candidates(word, words_freq):
    "Generate possible spelling corrections for word."
    return known([word], words_freq) or known(edits1(word), words_freq) \
                or known(edits2(word), words_freq) or [word]

def known(words, words_freq):
    "The subset of `words` that appear in the dictionary of WORDS."
    res = set()
    for word in words:
        if word in words_freq:
            res.update(words_freq[word].keys())
    return res

def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyz'
    splits = [(word[:i], word[i:])        for i in range(len(word) + 1)]
    deletes = [L + R[1:]                  for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:]             for L, R in splits if R for c in letters]
    inserts = [L + c + R                  for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def next_word_on_sentence(next_words):
    "Next word or punctuation on sentence."
    for word in next_words:
        if not regex.search(r'\s+', word):
            return word
    return None

def correct_line(line, pos_freqs, words_freq, nlp):
    "Corrects words on `line`."
    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = ''
    flatten = lambda l: [item for sublist in l for item in sublist]
    n_words = sum(flatten(map(lambda x: x.values(), words_freq.values())))
    last_word = None
    exceptions = ['sr', 'sra', 'sras', 'dr', 'dra', 'prof']
    for i, word in enumerate(words):
        if word.isspace():
            new_line += regex.sub(r' +', ' ', word)
        elif regex.search(r'\p{P}+', word, flags=regex.UNICODE) or not word.isalpha():
            new_line += word
        else:
            # candidates = candidates(word, words_freq)
            before_word = last_word
            after_word = next_word_on_sentence(words[i+1:])
            last_word = correction(word.lower(), words_freq, pos_freqs, n_words, before_word,
                                   after_word, nlp)
            new_line += last_word
    # Caracter maiúsculo no início da linha
    new_line = regex.sub(r'^\s*\w', lambda x: x[0].upper(), new_line)
    # Caracter maiúsculo após sinal de pontuação
    new_line = regex.sub(r'(?<=[^(?:' + r'|'.join(exceptions) + r')][\.!?])\s*\w',
                         lambda x: x[0].upper(), new_line)
    return new_line


####################             ASPELL              ####################

def correct_line_aspell(line):
    "Corrects words on `line`, using aspell library."
    speller = aspell.Speller('lang', 'pt_PT')
    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word) or not word.isalpha():
            new_line.append(word)
        else:
            suggestions = speller.suggest(word)
            if suggestions:
                new_line.append(suggestions[0])
            else:
                new_line.append(word)
    return ''.join(new_line)


####################            HUNSPELL             ####################

def correct_line_hunspell(line):
    "Corrects words on `line`, using hunspell library."
    hobj = hunspell.HunSpell('dictionaries/hunspell-pt_PT-20171225/pt_PT.dic',
                             'dictionaries/hunspell-pt_PT-20171225/pt_PT.aff')
    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word) or not word.isalpha():
            new_line.append(word)
        elif hobj.spell(word):
            new_line.append(word)
        else:
            suggestions = hobj.suggest(word)
            if suggestions:
                new_line.append(suggestions[0])
            else:
                new_line.append(word)
    return ''.join(new_line)


####################            SYMSPELL            #####################

def correct_line_symspell(line):
    "Corrects words on `line`, using symspell library."
    # create object
    initial_capacity = 83000
    max_edit_distance_dictionary = 2 # maximum edit distance per dictionary precalculation
    prefix_length = 7
    sym_spell = SymSpell(initial_capacity, max_edit_distance_dictionary, prefix_length)

    # load dictionary
    dictionary_path = os.path.join(os.path.dirname(__file__), "dictionaries/pt_PT-freq.txt")
    term_index = 0  # column of the term in the dictionary text file
    count_index = 1  # column of the term frequency in the dictionary text file
    if not sym_spell.load_dictionary(dictionary_path, term_index, count_index):
        print("ERROR: Dictionary file not found", file=sys.stderr)
        return line

    # lookup suggestions for single-word input strings
    max_edit_distance_lookup = 2
    suggestion_verbosity = Verbosity.CLOSEST  # TOP, CLOSEST, ALL

    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word) or not word.isalpha():
            new_line.append(word)
        else:
            suggestions = sym_spell.lookup(word, suggestion_verbosity, max_edit_distance_lookup)
            if suggestions:
                new_line.append(suggestions[0].term)
            else:
                new_line.append(word)
    new_line = ''.join(new_line)

    new_line = regex.sub(r'^\s*\w', lambda x: x[0].upper(), new_line)
    # Caracter maiúsculo após sinal de pontuação
    exceptions = ['sr', 'sra', 'sras', 'dr', 'dra', 'prof']
    new_line = regex.sub(r'(?<=[^(?:' + r'|'.join(exceptions) + r')][\.!?])\s*\w',
                         lambda x: x[0].upper(), new_line)
    return new_line


####################           POS TAGGING           ####################

def exists(ordered_list, elem):
    "Verifies if `elem` exists on `ordered_list`."
    i = bisect.bisect_left(ordered_list, elem)
    return bool(i != len(ordered_list) and ordered_list[i] == elem)

# python -m spacy download pt
def get_pos_frequences(text_fd, dict_words):
    "Get POS 3-tuples and words frequences, processing train text."
    nlp = spacy.load('pt')
    pos_freq = Counter()
    words = defaultdict(Counter)
    lines = text_fd.readlines()
    n_lines = len(lines)
    for n_line, line in enumerate(lines):
        doc = nlp(line)
        added_words = []
        for word_doc in doc:
            # Pré-Requisito: Dicionário tem de estar ordenado
            word = str(word_doc)
            word_first_lower = None if word[0].islower() else word[0].lower() + word[1:]
            if exists(dict_words, word):
                words[word.lower()][word] += 1
                added_words.append(word_doc)
            elif word_first_lower and exists(dict_words, word_first_lower):
                words[word.lower()][word_first_lower] += 1
                added_words.append(word_doc)
        len_doc = len(doc)
        for i in range(1, len_doc-1):
            doc_0 = doc[i-1].pos_ + get_tag(doc[i-1]) \
                    if doc[i-1] in added_words or doc[i-1].pos_ == 'PUNCT' \
                    else '<UNKNOWN>'
            doc_1 = doc[i].pos_ + get_tag(doc[i]) \
                    if doc[i] in added_words or doc[i].pos_ == 'PUNCT' \
                    else '<UNKNOWN>'
            doc_2 = doc[i+1].pos_ + get_tag(doc[i+1]) \
                    if doc[i+1] in added_words or doc[i+1].pos_ == 'PUNCT' \
                    else '<UNKNOWN>'
            if doc_1 != '<UNKNOWN>':
                pos_freq[doc_0 + ' ' + doc_1 + ' ' + doc_2] += 1
                if doc_0 != '<UNKNOWN>' and doc_2 != '<UNKNOWN>':
                    pos_freq['<UNKNOWN>' + ' ' + doc_1 + ' ' + doc_2] += 1
                    pos_freq[doc_0 + ' ' + doc_1 + ' ' + '<UNKNOWN>'] += 1

        print(f'Processado {str(n_line)}/{str(n_lines)}', end='\r', file=sys.stderr)
    # Adiciona uma entrada para cada palavra do dicionário
    for word in dict_words:
        words[word.lower()][word] += 1

    return pos_freq, words

def analyze_large_text():
    "Process train text or load result of previous analsis."
    # iconv -f ISO-8859-1 -t UTF-8//TRANSLIT CETEMPublico1.7_100MB -o CETEMPublico_100MB_.txt

    # cat CETEMPublico_100MB_.txt | perl -pe 's/\s/ /g' | perl -pe 's/\s*<[^>]+>\s*/\n/g' | \
    # perl -pe 's/^\s*$//g' | perl -pe 's/ +/ /g' | perl -pe 's/ ([,.!?$%;:])/\1/g' | \
    # perl -pe 's/(\(|\[|\{|«|<) /\1/g' | perl -pe 's/ (\)|\]|\}|>|»)/\1/g' > CETEMPublico.txt
    if not os.path.isfile('dict_info_tags.json'):
        pos_freq = None
        words_freq = None
        with open('dictionaries/wordlist-ao-latest.txt') as dict_fd:
            dict_words = dict_fd.read().splitlines()
            dict_words.sort()
            with open('CETEMPublico_20MB.txt') as text_fd:
                pos_freq, words_freq = get_pos_frequences(text_fd, dict_words)
        with open('dict_info_tags.json', 'w') as file_desc:
            json.dump((pos_freq, words_freq), file_desc)
    else:
        with open('dict_info_tags.json', 'r') as file_desc:
            (pos_freq, words_freq) = json.load(file_desc)
    return pos_freq, words_freq


####################             CORRECT             ####################

def correct_text_files(args, pos_freq, words_freq, correct_function):
    "Corrects text of files, with manual mode."
    nlp = spacy.load('pt')
    for line in fileinput.input(args):
        new_line = correct_function(line.strip(), pos_freq, words_freq, nlp)
        print(new_line)


def correct_text_files_ext(args, correct_function):
    "Corrects text of files, with aspell, hunspell or symspell (`correct_function`) mode."
    for line in fileinput.input(args):
        new_line = correct_function(line.strip())
        print(new_line)


def correct_text(pos_freq, words_freq, text_lines):
    "Corrects text lines, with manual mode."
    new_text = []
    nlp = spacy.load('pt')
    for line in text_lines:
        new_text.append(correct_line(line.strip(), pos_freq, words_freq, nlp))
    return '\n'.join(new_text)


def correct_text_ext(text_lines, correct_function):
    "Corrects text lines, with aspell, hunspell or symspell (`correct_function`) mode."
    new_text = []
    for line in text_lines:
        new_text.append(correct_function(line.strip()))
    return '\n'.join(new_text)


####################              MAIN               ####################

def main():
    "Main function."
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvm:", ["help", "version", "mode="])
    except getopt.GetoptError:
        print('USAGE: python3 spellcorrector.py [-h | -v | -m <CORRECT_MODE>] <INPUT_FILEAME> ' +\
                '<INPUT_FILEAME> ...\n' +\
                'OPTIONS:\n' +\
                '\t-h, --help\tShows this menu\n' +\
                '\t-v, --version\tShows program version\n' +\
                '\t-m, --mode\tUses specified mode - aspell, hunspell or symspell - ' +\
                    'to correct text words')
        exit(1)

    correct_function = correct_line
    for opt, arg in opts:
        if opt in ('-m', '--mode'):
            if arg == 'aspell':
                correct_function = correct_line_aspell
            elif arg == 'hunspell':
                correct_function = correct_line_hunspell
            elif arg == 'symspell':
                correct_function = correct_line_symspell
            else:
                print(f'ERROR: Mode name ({arg}) not recognized', file=sys.stderr)
                exit(1)
        if opt in ('-h', '--help'):
            print('USAGE: python3 spellcorrector.py [-h | -v | -m <CORRECT_MODE>] ' +\
                '<INPUT_FILEAME> <INPUT_FILEAME> ...\n' +\
                    'OPTIONS:\n' +\
                    '\t-h, --help\tShows this menu\n' +\
                    '\t-v, --version\tShows program version\n' +\
                    '\t-m, --mode\tUses specified mode - aspell, hunspell or symspell - ' +\
                        'to correct text words')
            exit(0)
        if opt in ('-v', '--version'):
            print('spellcorrector v1.0')
            exit(0)

    if correct_function == correct_line:
        print('--Geração de Estatísticas Iniciada--', file=sys.stderr)
        time1 = time.time()
        pos_freq, words_freq = analyze_large_text()
        time2 = time.time()
        print('--Geração de Estatísticas Terminada--', file=sys.stderr)
        print('\n--Processamento de texto Iniciado--', file=sys.stderr)
        correct_text_files(args, pos_freq, words_freq, correct_function)
        time3 = time.time()
        print('--Processamento de texto Terminado--', file=sys.stderr)

        print(file=sys.stderr)
        print('Time Load:\t %.2f sec' % (time2-time1), file=sys.stderr)
        print('Time Correct:\t %.2f sec' % (time3-time2), file=sys.stderr)

    else:
        time1 = time.time()
        correct_text_files_ext(args, correct_function)
        time2 = time.time()
        print('Time Correct:\t %.2f sec' % (time2-time1), file=sys.stderr)


if __name__ == "__main__":
    main()

__author__ = "João Barreira, Mafalda Nunes"
__email__ = "a73831@alunos.uminho.pt, a77364@alunos.uminho.pt"
