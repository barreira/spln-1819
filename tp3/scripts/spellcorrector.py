import re
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

#################### VERSÃO COM EXPRESSÕES REGULARES ####################

def words(text): return re.findall(r'\w+', text.lower())

# WORDS = Counter(words(open('dictionaries/wordlist-ao-latest.txt').read()))

def P(word, words_freq, pos_freqs, N_pos, context_pos): 
    "Probability of `word`."
    if word in words_freq:
        freq = words_freq[word.lower()][word] / N_pos
    else:
        freq = 0
    if context_pos:
        pos_freq = pos_freqs[context_pos] / sum(pos_freqs.values())
        freq *= pos_freq
    return freq

def correction(word, words_freq, pos_freqs, N_pos, context_pos): 
    "Most probable spelling correction for word."
    return max(candidates(word, words_freq), key=lambda x: P(x, words_freq, pos_freqs, N_pos, context_pos))

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

def correct_line(line, pos_freqs, words_freq):
    # TODO: Pré-processar: espaços
    # TODO: Pós-processar: tracinhos
    nlp = spacy.load('pt')
    doc = nlp(line)
    words =  re.findall(r'\w+|\W+', line, flags=re.UNICODE)
    new_line = ''
    i = 0
    n = len(doc)
    flatten = lambda l: [item for sublist in l for item in sublist]
    N_pos = sum(flatten(map(lambda x: x.values() , words_freq.values())))
    for word in words:
        if all([c.isspace() or c in string.punctuation for c in word]):
            new_line += re.sub(r' +', ' ', word)
        else:
            # candidates = candidates(word, words_freq)
            if i == 0:
                context_pos = '__BEGIN__ ' + doc[0].pos_ + ' ' + doc[1].pos_
            elif i!=n-1:
                context_pos = doc[i-1].pos_ + ' ' + doc[i].pos_ + ' ' + doc[i+1].pos_
            else:
                context_pos = doc[i-1].pos_ + ' ' + doc[i].pos_ + ' __END__'
            new_line += correction(word.lower(), words_freq, pos_freqs, N_pos, context_pos)
            i += 1
    exceptions = ['sr','sra','sras','dr','dra','prof']
    # Caracter maiúsculo no início da linha
    new_line = re.sub(r'^\s*\w', lambda x: x[0].upper(), new_line)
    # Caracter maiúsculo após sinal de pontuação
    new_line = re.sub(r'(?<=[^(?:' + r'|'.join(exceptions) + r')][\.!?])\s*\w', lambda x: x[0].upper(), new_line)
    return new_line



####################             ASPELL              ####################

def correct_line_aspell(line):
    s = aspell.Speller('lang', 'pt_PT')
    words = re.split(r'\s+', line)
    new_line = []
    for word in words:
        if word in string.punctuation:
            new_line.append(word)
        else:
            new_line.append(s.suggest(word)[0])
    return ' '.join(new_line)


####################            HUNSPELL             ####################
def correct_line_hunspell(line):
    hobj = hunspell.HunSpell('dictionaries/hunspell-pt_PT-20171225/pt_PT.dic', 'dictionaries/hunspell-pt_PT-20171225/pt_PT.aff')
    words = re.split(r'\s+', line)
    new_line = []
    for word in words:
        if word in string.punctuation:
            new_line.append(word)
        else:
            new_line.append(hobj.suggest(word)[0])
    return ' '.join(new_line)



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
        print("Dictionary file not found")
        return

    # lookup suggestions for single-word input strings
    # input_term = "memebers"
    # max_edit_distance_lookup = 2
    # suggestion_verbosity = Verbosity.CLOSEST  # TOP, CLOSEST, ALL
    # suggestions = sym_spell.lookup(input_term, suggestion_verbosity, max_edit_distance_lookup)
    # for suggestion in suggestions:
    #     print("{}, {}, {}".format(suggestion.term, suggestion.count, suggestion.distance))

    # lookup suggestions for multi-word input strings (supports compound splitting & merging)
    max_edit_distance_lookup = 2
    suggestions = sym_spell.lookup_compound(line, max_edit_distance_lookup)
    return ' | '.join([ suggestion.term for suggestion in suggestions ])
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
    # lines = text_fd.readlines()
    # n_lines = len(lines)
    # for n_line, line in enumerate(lines):
    for line in text_fd:
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
        if doc[0] in added_words and doc[1] in added_words:
            c['__BEGIN__ ' + doc[0].pos_ + ' ' + doc[1].pos_] += 1
        for i in range(1,len_doc-1):
            if doc[i-1] in added_words and doc[i] in added_words and doc[i+1] in added_words: 
                c[doc[i-1].pos_ + ' ' + doc[i].pos_ + ' ' + doc[i+1].pos_] += 1
        if doc[len_doc-2] in added_words and doc[len_doc-1] in added_words:
            c[doc[len_doc-2].pos_ + ' ' + doc[len_doc-1].pos_ + ' __END__'] += 1
        #print(f'Processado {str(n_line)}/{str(n_lines)}', end='\r')
    # Adiciona uma entrada para cada palavra do dicionário
    for word in dict_words:
        words[word.lower()][word] += 1

    return c, words

def analyze_large_text():
    # cat CETEMPublico1.7_100MB | perl -pe 's/\s/ /g' | perl -pe 's/\s*<[^>]+>\s*/\n/g' | perl -pe 's/^\s*$//g' | perl -pe 's/ ([,.!?$%;:])/\1/g' | perl -pe 's/(\(|\[|\{|«|<) /\1/g' | perl -pe 's/ (\)|\]|\}|>|»)/\1/g' > CETEMPublico.txt
    if not os.path.isfile('dict_info.json'):
        pos_freq = None
        words_freq = None
        with open('dictionaries/wordlist-ao-latest.txt') as dict_fd:
            dict_words = dict_fd.read().splitlines()
            dict_words.sort()
            with open('CETEMPublico_20MB.txt') as text_fd:
                pos_freq, words_freq = get_pos_frequences(text_fd, dict_words)
        with open('dict_info.json', 'w' ) as fd:
            json.dump((pos_freq, words_freq), fd)
    else:
        with open('dict_info.json', 'r' ) as fd:
            (pos_freq, words_freq) = json.load(fd)
    return pos_freq, words_freq


####################              MAIN               ####################
def main():
    # opts, args = getopt.getopt(sys.argv[1:], "bhv", ["build", "help", "version"])
    # opts_dict = dict(opts)

    print('--Geração de Estatísticas Iniciada--', file=sys.stderr)
    t1 = time.time()
    pos_freq, words_freq = analyze_large_text()
    t2 = time.time()
    print('--Geração de Estatísticas Terminada--', file=sys.stderr)
    print('\n--Processamento de texto Iniciado--', file=sys.stderr)
    new_text = []
    for line in fileinput.input():
        new_text.append(correct_line(line.strip(), pos_freq, words_freq))
    t3 = time.time()
    print('\n'.join(new_text))
    print('--Processamento de texto Terminado--', file=sys.stderr)

    print(file=sys.stderr)
    print('Time Load:\t %.2f sec' % (t2-t1), file=sys.stderr)
    print('Time Correct:\t %.2f sec' % (t3-t2), file=sys.stderr)


if __name__ == "__main__":
    main()