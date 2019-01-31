# coding=utf-8
#!/usr/bin/python3

''' Measure metrics (5 tests average) from spellcorrector.py, with several operation modes

Indicates several metrics (avarage) for each operation mode ("Manual", Aspell, Hunspell and
Symspell):
    * True Positives Wrong
    * True Positives Right
    * True Negatives
    * False Positives
    * False Negatives
    * Accuracy
    * Precision
    * Recall
    * Harmonic Mean
    * True Positives Rate
    * False Positives Rate
    * Execution Duration (sec)
'''

import sys
import time
import fileinput

import regex
import numpy as np
from prettytable import PrettyTable

import spellcorrector

def is_word(token):
    "Indicates if token is a `word`."
    return bool(regex.search(r'\w+', token, flags=regex.UNICODE))

def process_token(token):
    "Process token."
    if len(token) <= 3:
        n_changes = np.random.choice([0, 1], p=[3.0/4.0, 1.0/4.0])
    else:
        n_changes = np.random.choice([0, 1, 2], p=[3.0/4.0, 0.8/4.0, 0.2/4.0])

    changes = np.random.choice([1, 2, 3, 4], size=(n_changes))
    for change in changes:
        if change == 1: # delete
            if len(token) > 1:
                i_rand = np.random.randint(0, len(token))
                token = token[0:i_rand] + token[i_rand+1:]
        elif change == 2: # transposes (i <-> i+1)
            if len(token) > 1:
                i_rand = np.random.randint(0, len(token)-1)
                token = token[0:i_rand] + token[i_rand+1] + token[i_rand] + token[i_rand+2:]
        elif change == 3: # replaces
            i_rand = np.random.randint(0, len(token))
            new_char = np.random.choice(list('aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyz' +\
                                             'AÁÀÃÂBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÕÔPQRSTUÚÙÛVWXYZ'))
            token = token[0:i_rand] + new_char + token[i_rand+1:]
        else: # inserts
            i_rand = np.random.randint(0, len(token))
            new_char = np.random.choice(list('aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyz' +\
                                             'AÁÀÃÂBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÕÔPQRSTUÚÙÛVWXYZ'))
            token = token[0:i_rand] + new_char + token[i_rand:]
    return token


def gen_text_with_errors(tokens):
    "Generate text with errors, from `tokens` list."
    errors_tokens = []
    for token in tokens:
        if is_word(token) and len(token) > 1:
            errors_tokens.append(process_token(token))
        else:
            errors_tokens.append(token)

    return ''.join(errors_tokens)


def classification(original_word, errors_word, corrected_word):
    "Classify spell correction as TPW, TPR, TN, FP or FN."
    # True Positives
    if original_word != errors_word and errors_word != corrected_word:
        # Correção errada
        if original_word != corrected_word:
            return 'TPW'
        # Correção correta
        return 'TPR'
    # True Negatives
    if original_word == errors_word and errors_word == corrected_word:
        return 'TN'
    # False Positives
    if original_word == errors_word and errors_word != corrected_word:
        return 'FP'
    # False Negatives
    if original_word != errors_word and errors_word == corrected_word:
        return 'FN'
    return None


def get_wrong_texts(n_tests, original_tokens):
    "Get `n_tests` texts with errors."
    wrong_texts = []
    with open('metrics_errors.txt', 'w+') as file_desc:
        for i in range(n_tests):
            errors_text = gen_text_with_errors(original_tokens)
            wrong_texts.append(errors_text)
            print(f'\n-- TESTE {i} --', file=file_desc)
            print(errors_text, file=file_desc)
    return wrong_texts


def get_metrics(function_name, id_test, function, original_tokens, errors_text):
    "Calculates metrics."
    errors_tokens = regex.findall(r'\w+|\s+|\p{P}+', errors_text, flags=regex.UNICODE)

    # Corrigir erros do texto
    print(f'-- Correção dos erros do texto com função {function_name} - Teste {str(id_test)} --',
          file=sys.stderr)
    if function_name == 'Manual':
        time1 = time.time()
        pos_freq, words_freq = spellcorrector.analyze_large_text()
        time2 = time.time()
        corrected_text = spellcorrector.correct_text(pos_freq, words_freq,
                                                     text_lines=errors_text.split('\n'))
        time3 = time.time()
        duration = (time2-time1, time3-time2)
    else:
        time1 = time.time()
        corrected_text = spellcorrector.correct_text_ext(errors_text.split('\n'), function)
        time2 = time.time()
        duration = time2-time1

    corrected_tokens = regex.findall(r'\w+|\s+|\p{P}+', corrected_text, flags=regex.UNICODE)
    with open('metrics_corrected.txt', 'a+') as file_desc:
        print(f'\n-- FUNÇÃO {function_name} - TESTE {id_test} --', file=file_desc)
        print(corrected_text, file=file_desc)

    # Calcular métricas
    print('-- Cálculo de métricas --', file=sys.stderr)
    true_positives_wrong_correction = 0  # Há erro e token é corrigido incorretamente
    true_positives_right_correction = 0  # Há erro e token é corrigido corretamente
    true_negatives = 0  # Não há erro e token mantém-se
    false_positives = 0 # Não há erro, mas token é corrigido
    false_negatives = 0 # Há erro, mas este não é corrigido
    total_words = 0

    for i, token in enumerate(original_tokens):
        if is_word(token) or is_word(errors_tokens[i]) or is_word(corrected_tokens[i]):
            total_words += 1
            classif = classification(token, errors_tokens[i], corrected_tokens[i])
            # True Positives, Correção errada
            if classif == 'TPW':
                true_positives_wrong_correction += 1
            # True Positives, Correção correta
            elif classif == 'TPR':
                true_positives_right_correction += 1
            # True Negatives
            elif classif == 'TN':
                true_negatives += 1
            # False Positives
            elif classif == 'FP':
                false_positives += 1
            # False Negatives
            elif classif == 'FN':
                false_negatives += 1

    return true_positives_wrong_correction, true_positives_right_correction, true_negatives, \
           false_positives, false_negatives, total_words, duration


def run_tests(function_name, function, original_tokens, wrong_texts, n_tests):
    "Run tests."
    true_positives_wrong_correction = 0  # Há erro e token é corrigido incorretamente
    true_positives_right_correction = 0  # Há erro e token é corrigido corretamente
    true_negatives = 0  # Não há erro e token mantém-se
    false_positives = 0 # Não há erro, mas token é corrigido
    false_negatives = 0 # Há erro, mas este não é corrigido
    total_words = 0
    duration = 0

    for i in range(0, n_tests):
        m_tpw, m_tpr, m_tn, m_fp, m_fn, m_tw, m_d = get_metrics(function_name, i, function,
                                                                original_tokens, wrong_texts[i])
        true_positives_wrong_correction += m_tpw
        true_positives_right_correction += m_tpr
        true_negatives += m_tn
        false_positives += m_fp
        false_negatives += m_fn
        total_words += m_tw
        if isinstance(m_d, tuple):
            if i == 0:
                duration = [m_d[0], m_d[1]]
            else:
                duration[0] += m_d[0]
                duration[1] += m_d[1]
        else:
            duration += m_d

    true_positives_wrong_correction /= n_tests
    true_positives_right_correction /= n_tests
    true_negatives /= n_tests
    false_positives /= n_tests
    false_negatives /= n_tests
    total_words /= n_tests
    if isinstance(duration, list):
        duration[0] /= n_tests
        duration[1] /= n_tests
    else:
        duration /= n_tests

    true_positives = true_positives_right_correction + true_positives_wrong_correction

    if total_words > 0:
        accuracy = round((true_positives_right_correction + true_negatives) / total_words, 2)

        if true_positives + false_positives > 0:
            precision = round(true_positives_right_correction / (true_positives + false_positives),
                              2)
        else:
            precision = None

        if true_positives + false_negatives > 0:
            recall = round(true_positives_right_correction / (true_positives + false_negatives), 2)
        else:
            recall = None

        if precision and recall and precision + recall > 0:
            harmonic_mean = round(2 * ((precision * recall) / (precision + recall)), 2)
        else:
            harmonic_mean = None

        if true_positives + false_negatives > 0:
            true_positive_rate = round(true_positives_right_correction /
                                       (true_positives + false_negatives), 2)
        else:
            true_positive_rate = None

        if false_positives + true_negatives > 0:
            false_positive_rate = round(false_positives / (false_positives + true_negatives), 2)
        else:
            false_positive_rate = None
    else:
        accuracy = None
        precision = None
        recall = None
        harmonic_mean = None
        true_positive_rate = None
        false_positive_rate = None

    return true_positives_wrong_correction, true_positives_right_correction, true_negatives,\
            false_positives, false_negatives, accuracy, precision, recall, harmonic_mean,\
            true_positive_rate, false_positive_rate, duration


def main():
    "Main function."
    # Ler texto correto
    print('-- Leitura do texto correto --', file=sys.stderr)
    original_text = ''.join([line for line in fileinput.input(sys.argv[1:])])
    original_tokens = regex.findall(r'\w+|\s+|\p{P}+', original_text, flags=regex.UNICODE)

    print('-- Inserção de erros no texto original (5x) --', file=sys.stderr)
    wrong_texts = get_wrong_texts(5, original_tokens)

    # Gerar estrutura da tabela output
    table = PrettyTable()
    table.field_names = ["Medidas", "Manual", "Aspell", "Hunspell", "Symspell"]
    tpw_list = ['True Positives Wrong']
    tpr_list = ['True Positives Right']
    tn_list = ['True Negatives']
    fp_list = ['False Positives']
    fn_list = ['False Negatives']
    accuracy_list = ['Accuracy']
    precision_list = ['Precision']
    recall_list = ['Recall']
    hm_list = ['Harmonic Mean']
    tp_rate_list = ['TP Rate']
    fp_rate_list = ['FP Rate']
    d_list = ['Duration (sec)']

    m_tpw, m_tpr, m_tn, m_fp, m_fn, accuracy, precision, recall, h_mean, tp_rate, fp_rate, dur = \
        run_tests('Manual', spellcorrector.correct_text, original_tokens, wrong_texts, 5)
    tpw_list.append(m_tpw)
    tpr_list.append(m_tpr)
    tn_list.append(m_tn)
    fp_list.append(m_fp)
    fn_list.append(m_fn)
    accuracy_list.append(accuracy)
    precision_list.append(precision)
    recall_list.append(recall)
    hm_list.append(h_mean)
    tp_rate_list.append(tp_rate)
    fp_rate_list.append(fp_rate)
    d_list.append(f'{round(dur[0],2)} + {round(dur[1],2)}')

    function_names = ["Aspell", "Hunspell", "Symspell"]
    functions = [spellcorrector.correct_line_aspell, spellcorrector.correct_line_hunspell,
                 spellcorrector.correct_line_symspell]
    for i in range(0, 3):
        m_tpw, m_tpr, m_tn, m_fp, m_fn, accuracy, precision, recall, h_mean, tp_rate, fp_rate, \
            dur = run_tests(function_names[i], functions[i], original_tokens, wrong_texts, 5)
        tpw_list.append(m_tpw)
        tpr_list.append(m_tpr)
        tn_list.append(m_tn)
        fp_list.append(m_fp)
        fn_list.append(m_fn)
        accuracy_list.append(accuracy)
        precision_list.append(precision)
        recall_list.append(recall)
        hm_list.append(h_mean)
        tp_rate_list.append(tp_rate)
        fp_rate_list.append(fp_rate)
        d_list.append(str(round(dur, 2)))

    table.add_row(tpw_list)
    table.add_row(tpr_list)
    table.add_row(tn_list)
    table.add_row(fp_list)
    table.add_row(fn_list)
    table.add_row(accuracy_list)
    table.add_row(precision_list)
    table.add_row(recall_list)
    table.add_row(hm_list)
    table.add_row(tp_rate_list)
    table.add_row(fp_rate_list)
    table.add_row(d_list)

    print(table)


if __name__ == "__main__":
    main()

__author__ = "João Barreira, Mafalda Nunes"
__email__ = "a73831@alunos.uminho.pt, a77364@alunos.uminho.pt"
