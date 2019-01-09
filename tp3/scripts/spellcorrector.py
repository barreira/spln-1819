import re
import os
import pickle
import bisect
import spacy
import fileinput
import string
import aspell
import hunspell
from collections import Counter
from symspellpy.symspellpy import SymSpell, Verbosity

#################### VERSÃO COM EXPRESSÕES REGULARES ####################

def words(text): return re.findall(r'\w+', text.lower())

# WORDS = Counter(words(open('dictionaries/wordlist-ao-latest.txt').read()))

def P(word, words_dict, pos_freqs, context_pos): 
    "Probability of `word`."
    N=sum(words_dict.values())
    freq = words_dict[word] / N
    if context_pos:
        pos_freq = pos_freqs[context_pos] / sum(pos_freqs.values())
        freq *= pos_freq
    return freq

def correction(word, words_dict, pos_freqs, context_pos): 
    "Most probable spelling correction for word."
    return max(candidates(word, words_dict), key=lambda x: P(x, words_dict, pos_freqs, context_pos))

def candidates(word, words_dict): 
    "Generate possible spelling corrections for word."
    return (known([word], words_dict) or known(edits1(word), words_dict) or known(edits2(word), words_dict) or [word])

def known(words, words_dict): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in words_dict)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def correct_line(line, pos_freqs, words_dict):
    # TODO: Pré-processar: espaços
    # TODO: Pós-processar: tracinhos
    nlp = spacy.load('pt')
    doc = nlp(line)
    words = re.findall(r'(\w+|[' + string.punctuation + r']+)', line, flags=re.UNICODE)
    new_line = []
    n = len(doc)
    for i, word in enumerate(words):
        if word in string.punctuation:
            new_line.append(word)
        else:
            # candidates = candidates(word, words_dict)
            if i == 0:
                context_pos = '__BEGIN__ ' + doc[0].pos_ + ' ' + doc[1].pos_
            elif i==n-1:
                context_pos = doc[i-1].pos_ + ' ' + doc[i].pos_ + ' __END__'
            else:
                context_pos = doc[i-1].pos_ + ' ' + doc[i].pos_ + ' ' + doc[i+1].pos_
            new_line.append(correction(word.lower(), words_dict, pos_freqs, context_pos))
    return ' '.join(new_line)



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
    words = Counter()
    lines = text_fd.readlines()
    # n_lines = len(lines)
    for n_line, line in enumerate(lines):
        doc = nlp(line)
        len_doc = len(doc)
        added_words = []
        for word in doc:
            # Pré-Requisito: Dicionário tem de estar ordenado
            if exists(dict_words, str(word)):
                words[str(word)] += 1
                added_words.append(word)
        c['__BEGIN__ ' + doc[0].pos_ + ' ' + doc[1].pos_] += 1
        for i in range(1,len_doc-1):
            if doc[i-1] in added_words and doc[i] in added_words and doc[i+1] in added_words: 
                c[doc[i-1].pos_ + ' ' + doc[i].pos_ + ' ' + doc[i+1].pos_] += 1
        c[doc[len_doc-2].pos_ + ' ' + doc[len_doc-1].pos_ + ' __END__'] += 1
        # print(f'Processado {str(n_line)}/{str(n_lines)}', end='\r')
    print('-- Processamento de Dicionário e Texto Terminado --')
    # Adiciona uma entrada para cada palavra do dicionário
    for word in dict_words:
        words[str(word)] += 1
    return c, words

def analyze_large_text():
    # cat CETEMPublico1.7_100MB | perl -pe 's/\s/ /g' | perl -pe 's/\s*<[^>]+>\s*/\n/g' | perl -pe 's/^\s*$//g' | perl -pe 's/ ([,.!?$%;:])/\1/g' | perl -pe 's/(\(|\[|\{|«|<) /\1/g' | perl -pe 's/ (\)|\]|\}|>|»)/\1/g' > CETEMPublico.txt
    if not os.path.isfile('dict_info.p'):
        pos_freq = None
        words_dict = None
        print('-- Leitura de Dicionário Iniciada --')
        with open('dictionaries/wordlist-ao-latest.txt') as dict_fd:
            dict_words = dict_fd.read().splitlines()
            dict_words.sort()
            print('-- Leitura de Texto de Treino Iniciada --')
            with open('CETEMPublico_20MB.txt') as text_fd:
                pos_freq, words_dict = get_pos_frequences(text_fd, dict_words)
        pickle.dump((pos_freq, words_dict), open('dict_info.p', 'wb' ))
    else:
        (pos_freq, words_dict) = pickle.load(open('dict_info.p', 'rb' ))
    return pos_freq, words_dict


####################              MAIN               ####################
def main():
    pos_freq, words_dict = analyze_large_text()
    new_text = []
    for line in fileinput.input():
        new_text.append(correct_line(line, pos_freq, words_dict))
    print('\n'.join(new_text))


if __name__ == "__main__":
    main()