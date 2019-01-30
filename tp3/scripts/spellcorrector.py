import regex
import os
import sys
import pickle
import json
import getopt
import bisect
import spacy
import fileinput
import time
import string
import aspell
import hunspell
from collections import Counter, defaultdict
from symspellpy.symspellpy import SymSpell, Verbosity


def get_tag(token):
    tags = list(filter(lambda x: x[0]!='<' and x[-1]!='>' and x[0]!='@', token.tag_.split('|')))
    if token.pos_ == 'ADV':
        t = str(token)
        if t == 'agora' or t == 'hoje':
            tags += '|Present'
        elif t == 'anteontem' or t == 'antes' or t == 'ontem' or t == 'outrora':
            tags += '|Past'
        elif t == 'amanhã' or t == 'breve':
            tags += '|Future'
    return '<' + '|'.join(tags) + '>'

#################### VERSÃO MANUAL ####################

def words(text): return regex.findall(r'\w+', text.lower())

# WORDS = Counter(words(open('dictionaries/wordlist-ao-latest.txt').read()))

def get_pos_context(before_word, word, after_word, words_freq, nlp):
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
    

def P(word, original_word, words_freq, pos_freqs, N_pos, before_word, after_word, nlp): 
    "Probability of `word`."
    context_pos = get_pos_context(before_word, word, after_word, words_freq, nlp)
    if word in words_freq:
        freq = (words_freq[word.lower()][word] / N_pos) * (60 if word.lower() != original_word.lower() else 100)
    else:
        freq = 0
    if context_pos:
        pos_freq = (99 * pos_freqs.get(context_pos, 0) + 1) / sum(pos_freqs.values())
        freq = freq * pos_freq * 100
    return freq

def correction(word, words_freq, pos_freqs, N_pos, before_word, after_word, nlp): 
    "Most probable spelling correction for word."
    return max(candidates(word, words_freq), key=lambda x: P(x, word, words_freq, pos_freqs, N_pos, before_word, after_word, nlp))

def candidates(word, words_freq): 
    "Generate possible spelling corrections for word."
    return (known([word], words_freq) or known(edits1(word), words_freq) or known(edits2(word), words_freq) or [word])

def known(words, words_freq): 
    "The subset of `words` that appear in the dictionary of WORDS."
    res = set()
    for w in words:
        if w in words_freq:
            res.update(words_freq[w].keys())
    return res

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def next_word_on_sentence(current_word, next_words, exceptions):
    for i, word in enumerate(next_words):
        if not regex.search(r'\s+', word):
            return word
    return None

def correct_line(line, pos_freqs, words_freq, nlp=spacy.load('pt')):
    words =  regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = ''
    flatten = lambda l: [item for sublist in l for item in sublist]
    N_pos = sum(flatten(map(lambda x: x.values() , words_freq.values())))
    last_word = None
    exceptions = ['sr','sra','sras','dr','dra','prof']
    for i, word in enumerate(words):
        if word.isspace():
            new_line += regex.sub(r' +', ' ', word)
        elif regex.search(r'\p{P}+', word, flags=regex.UNICODE):
            new_line += word
        else:
            # candidates = candidates(word, words_freq)
            before_word = last_word
            after_word = next_word_on_sentence(word, words[i+1:], exceptions)
            last_word = correction(word.lower(), words_freq, pos_freqs, N_pos, before_word, after_word, nlp)
            new_line += last_word
    # Caracter maiúsculo no início da linha
    new_line = regex.sub(r'^\s*\w', lambda x: x[0].upper(), new_line)
    # Caracter maiúsculo após sinal de pontuação
    new_line = regex.sub(r'(?<=[^(?:' + r'|'.join(exceptions) + r')][\.!?])\s*\w', lambda x: x[0].upper(), new_line)
    return new_line



####################             ASPELL              ####################

def correct_line_aspell(line):
    s = aspell.Speller('lang', 'pt_PT')
    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word):
            new_line.append(word)
        else:
            suggestions = s.suggest(word)
            if len(suggestions) > 0:
                new_line.append(suggestions[0])
            else:
                new_line.append(word)
    return ''.join(new_line)


####################            HUNSPELL             ####################
def correct_line_hunspell(line):
    hobj = hunspell.HunSpell('dictionaries/hunspell-pt_PT-20171225/pt_PT.dic', 'dictionaries/hunspell-pt_PT-20171225/pt_PT.aff')
    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word):
            new_line.append(word)
        elif hobj.spell(word):
            new_line.append(word)
        else:
            suggestions = hobj.suggest(word)
            if len(suggestions) > 0:
                new_line.append(suggestions[0])
            else:
                new_line.append(word)
    return ''.join(new_line)


####################            SYMSPELLY            ####################
def correct_line_symspelly(line):
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
        print("ERROR: Dictionary file not found")
        return

    # lookup suggestions for single-word input strings
    max_edit_distance_lookup = 2
    suggestion_verbosity = Verbosity.CLOSEST  # TOP, CLOSEST, ALL

    words = regex.findall(r'\w+|\s+|\p{P}+', line, flags=regex.UNICODE)
    new_line = []
    for word in words:
        if regex.match(r'\s+|\p{P}+', word):
            new_line.append(word)
        else:
            suggestions = sym_spell.lookup(word, suggestion_verbosity, max_edit_distance_lookup)
            if len(suggestions) > 0:
                new_line.append(suggestions[0].term)
            else:
                new_line.append(word)
    new_line = ''.join(new_line)


    # lookup suggestions for multi-word input strings (supports compound splitting & merging)
    # tokens = regex.findall(r'[\p{P}\s]+|[\w\s]+', line, flags=regex.UNICODE)
    # max_edit_distance_lookup = 2
    # new_line = ''
    # for token in tokens:
    #     if regex.match(r'[\p{P}\s]+', token, flags=regex.UNICODE):
    #         new_line += token
    #     else:
    #         suggestions = sym_spell.lookup_compound(token, max_edit_distance_lookup)
    #         new_line += suggestions[0].term
    
    # Caracter maiúsculo no início da linha
    new_line = regex.sub(r'^\s*\w', lambda x: x[0].upper(), new_line)
    # Caracter maiúsculo após sinal de pontuação
    exceptions = ['sr','sra','sras','dr','dra','prof']
    new_line = regex.sub(r'(?<=[^(?:' + r'|'.join(exceptions) + r')][\.!?])\s*\w', lambda x: x[0].upper(), new_line)
    return new_line

    return new_line
    # suggestions = sym_spell.word_segmentation(line)
    # return suggestions.corrected_string


####################           POS TAGGING           ####################
# python -m spacy download pt
def exists(l, x):
    i = bisect.bisect_left(l, x)
    if i != len(l) and l[i] == x:
        return True
    else:
        return False

def get_pos_frequences(text_fd, dict_words):
    nlp = spacy.load('pt')
    c = Counter()
    words = defaultdict(Counter)
    lines = text_fd.readlines()
    n_lines = len(lines)
    for n_line, line in enumerate(lines):
    #for line in text_fd:
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
        for i in range(1,len_doc-1):
            doc_0 = doc[i-1].pos_ + get_tag(doc[i-1]) if doc[i-1] in added_words or doc[i-1].pos_=='PUNCT' else '<UNKNOWN>'
            doc_1 = doc[i].pos_ + get_tag(doc[i]) if doc[i] in added_words or doc[i].pos_=='PUNCT' else '<UNKNOWN>'
            doc_2 = doc[i+1].pos_ + get_tag(doc[i+1]) if doc[i+1] in added_words or doc[i+1].pos_=='PUNCT' else '<UNKNOWN>'
            if doc_1 != '<UNKNOWN>':
                c[doc_0 + ' ' + doc_1 + ' ' + doc_2] += 1
                if doc_0 != '<UNKNOWN>' and doc_2 != '<UNKNOWN>':
                    c['<UNKNOWN>' + ' ' + doc_1 + ' ' + doc_2] += 1
                    c[doc_0 + ' ' + doc_1 + ' ' + '<UNKNOWN>'] += 1
        
        print(f'Processado {str(n_line)}/{str(n_lines)}', end='\r', file=sys.stderr)
    # Adiciona uma entrada para cada palavra do dicionário
    for word in dict_words:
        words[word.lower()][word] += 1

    return c, words

def analyze_large_text():
    # cat CETEMPublico1.7_100MB | perl -pe 's/\s/ /g' | perl -pe 's/\s*<[^>]+>\s*/\n/g' | perl -pe 's/^\s*$//g' | perl -pe 's/ ([,.!?$%;:])/\1/g' | perl -pe 's/(\(|\[|\{|«|<) /\1/g' | perl -pe 's/ (\)|\]|\}|>|»)/\1/g' > CETEMPublico.txt
    if not os.path.isfile('dict_info_tags.json'):
        pos_freq = None
        words_freq = None
        with open('dictionaries/wordlist-ao-latest.txt') as dict_fd:
            dict_words = dict_fd.read().splitlines()
            dict_words.sort()
            with open('CETEMPublico_20MB.txt') as text_fd:
                pos_freq, words_freq = get_pos_frequences(text_fd, dict_words)
        with open('dict_info_tags.json', 'w' ) as fd:
            json.dump((pos_freq, words_freq), fd)
    else:
        with open('dict_info_tags.json', 'r' ) as fd:
            (pos_freq, words_freq) = json.load(fd)
    return pos_freq, words_freq


####################              MAIN               ####################
def correct_text_files(args, pos_freq, words_freq, correct_function):
    new_text = []
    nlp = spacy.load('pt')
    for line in fileinput.input(args):
        new_text.append(correct_function(line.strip(), pos_freq, words_freq, nlp))
    return '\n'.join(new_text)


def correct_text_files_ext(args, correct_function):
    new_text = []
    for line in fileinput.input(args):
        new_text.append(correct_function(line.strip()))
    return '\n'.join(new_text)


def correct_text(pos_freq, words_freq, text_lines):
    new_text = []
    nlp = spacy.load('pt')
    for line in text_lines:
        new_text.append(correct_line(line.strip(), pos_freq, words_freq, nlp))
    return '\n'.join(new_text)


def correct_text_ext(text_lines, correct_function):
    new_text = []
    for line in text_lines:
        new_text.append(correct_function(line.strip()))
    return '\n'.join(new_text)


def main():
    opts, args = getopt.getopt(sys.argv[1:], "bhvf", ["build", "help", "version", "function="])
    
    correct_function = correct_line
    for o, a in opts:
        if o in ('-f','--function'):
            if a == 'aspell':
                correct_function = correct_line_aspell
            elif a == 'hunspell':
                correct_function = correct_line_hunspell
            elif a == 'symspelly':
                correct_function = correct_line_symspelly
            else:
                print(f'ERROR: Nome de função ({a}) de correção desconhecido', file=sys.stderr)
                exit(1)

    if correct_function == correct_line:
        print('--Geração de Estatísticas Iniciada--', file=sys.stderr)
        t1 = time.time()
        pos_freq, words_freq = analyze_large_text()
        t2 = time.time()
        print('--Geração de Estatísticas Terminada--', file=sys.stderr)
        print('\n--Processamento de texto Iniciado--', file=sys.stderr)
        new_text = correct_text_files(args, pos_freq, words_freq, correct_function)
        t3 = time.time()
        print(new_text)
        print('--Processamento de texto Terminado--', file=sys.stderr)

        print(file=sys.stderr)
        print('Time Load:\t %.2f sec' % (t2-t1), file=sys.stderr)
        print('Time Correct:\t %.2f sec' % (t3-t2), file=sys.stderr)
    
    else:
        t1 = time.time()
        new_text = correct_text_files_ext(args, correct_function)
        t2 = time.time()
        print(new_text)
        print('Time Correct:\t %.2f sec' % (t2-t1), file=sys.stderr)


if __name__ == "__main__":
    main()