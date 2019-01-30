import sys
import time
import regex
import string
import fileinput
import numpy as np
import spellcorrector
from prettytable import PrettyTable

def is_word(token):
    if regex.search(r'\w+', token, flags=regex.UNICODE):
        return True
    else:
        return False
    
def process_token(token):
    if len(token) <=3:
        n_changes = np.random.choice([0,1], p=[3.0/4.0, 1.0/4.0])
    else:
        n_changes = np.random.choice([0,1,2], p=[3.0/4.0, 0.8/4.0, 0.2/4.0])

    changes = np.random.choice([1,2,3,4], size=(n_changes))
    for change in changes:
        if change == 1: # delete
            if len(token) > 1:
                i = np.random.randint(0,len(token))
                token = token[0:i] + token[i+1:]
        elif change == 2: # transposes (i <-> i+1)
            if len(token) > 1:
                i = np.random.randint(0,len(token)-1)
                token = token[0:i] + token[i+1] + token[i] + token[i+2:]
        elif change == 3: # replaces
            i = np.random.randint(0,len(token))
            new_char = np.random.choice(list(
                'aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyzAÁÀÃÂBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÕÔPQRSTUÚÙÛVWXYZ')
            )
            token = token[0:i] + new_char + token[i+1:]
        else: # inserts
            i = np.random.randint(0,len(token))
            new_char = np.random.choice(list(
                'aáàãâbcçdeéèêfghiíìîjklmnoóòõôpqrstuúùûvwxyzAÁÀÃÂBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÕÔPQRSTUÚÙÛVWXYZ')
            )
            token = token[0:i] + new_char + token[i:]
    return token


def gen_text_with_errors(tokens):
    errors_tokens = []
    for i in range(len(tokens)):
        if is_word(tokens[i]) and len(tokens[i])>1:
            errors_tokens.append(process_token(tokens[i]))
        else:
            errors_tokens.append(tokens[i])
    
    return ''.join(errors_tokens)


def classification(original_word, errors_word, corrected_word):
    # True Positives
    if original_word != errors_word and errors_word != corrected_word:
        # Correção errada
        if original_word != corrected_word:
            return 'TPW'
        # Correção correta
        else:
            return 'TPR'
    # True Negatives
    elif original_word == errors_word and errors_word == corrected_word:
        return 'TN'
    # False Positives
    elif original_word == errors_word and errors_word != corrected_word:
        return 'FP'
    # False Negatives
    elif original_word != errors_word and errors_word == corrected_word:
        return 'FN'
    else:
        return None


def get_wrong_texts(n_tests, original_tokens):
    wrong_texts = []
    with open('aux_files/errors.txt', 'w+') as fd:
        for i in range(n_tests):
            errors_text = gen_text_with_errors(original_tokens)
            wrong_texts.append(errors_text)
            print(f'\n-- TESTE {i} --', file=fd)
            print(errors_text, file=fd)
    return wrong_texts


def get_metrics(function_name, id_test, function, original_tokens, errors_text):
    errors_tokens = regex.findall(r'\w+|\s+|\p{P}+', errors_text, flags=regex.UNICODE)

    # Corrigir erros do texto
    print(f'-- Correção dos erros do texto com função {function_name} - Teste {str(id_test)} --', file=sys.stderr)
    if function_name == 'Manual':
        t1 = time.time()
        pos_freq, words_freq = spellcorrector.analyze_large_text()
        t2 = time.time()
        corrected_text = spellcorrector.correct_text(pos_freq, words_freq, text_lines=errors_text.split('\n'))
        t3 = time.time()
        duration = (t2-t1, t3-t2)
    else:
        t1 = time.time()
        corrected_text = spellcorrector.correct_text_ext(errors_text.split('\n'), function)
        t2 = time.time()
        duration = t2-t1

    corrected_tokens = regex.findall(r'\w+|\s+|\p{P}+', corrected_text, flags=regex.UNICODE)
    with open('aux_files/corrected.txt', 'a+') as fd:
        print(f'\n-- FUNÇÃO {function_name} - TESTE {id_test} --', file=fd)
        print(corrected_text, file=fd)

    # Calcular métricas
    # TODO: DUVIDA NAS METRICAS
    print('-- Cálculo de métricas --', file=sys.stderr)
    true_positives_wrong_correction = 0  # Há erro e token é corrigido incorretamente
    true_positives_right_correction = 0  # Há erro e token é corrigido corretamente
    true_negatives = 0  # Não há erro e token mantém-se
    false_positives = 0 # Não há erro, mas token é corrigido
    false_negatives = 0 # Há erro, mas este não é corrigido
    total_words = 0

    for i in range(len(original_tokens)):
        if is_word(original_tokens[i]) or is_word(errors_tokens[i]) or is_word(corrected_tokens[i]):
            total_words += 1
            c = classification(original_tokens[i], errors_tokens[i], corrected_tokens[i])
            # True Positives, Correção errada
            if c == 'TPW' :
                true_positives_wrong_correction += 1
            # True Positives, Correção correta
            elif c == 'TPR':
                true_positives_right_correction += 1
            # True Negatives
            elif c == 'TN':
                true_negatives += 1
            # False Positives
            elif c == 'FP':
                false_positives += 1
            # False Negatives
            elif c == 'FN':
                false_negatives += 1
    
    return true_positives_wrong_correction, true_positives_right_correction, true_negatives, false_positives, false_negatives, total_words, duration


def run_tests(function_name, function, original_tokens, wrong_texts, n_tests):
    true_positives_wrong_correction = 0  # Há erro e token é corrigido incorretamente
    true_positives_right_correction = 0  # Há erro e token é corrigido corretamente
    true_negatives = 0  # Não há erro e token mantém-se
    false_positives = 0 # Não há erro, mas token é corrigido
    false_negatives = 0 # Há erro, mas este não é corrigido
    total_words = 0
    duration = 0

    for i in range(0,n_tests):
        tpw, tpr, tn, fp, fn, tw, d = get_metrics(function_name, i, function, original_tokens, wrong_texts[i])
        true_positives_wrong_correction += tpw
        true_positives_right_correction += tpr
        true_negatives += tn
        false_positives += fp
        false_negatives += fn
        total_words += tw
        if isinstance(d, tuple):
            if i == 0:
                duration = [d[0],d[1]]
            else:
                duration[0] += d[0]
                duration[1] += d[1]
        else:
            duration += d
    
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
        accuracy = round( (true_positives_right_correction + true_negatives) / total_words, 2 )

        if true_positives + false_positives > 0:
            precision = round( true_positives_right_correction / (true_positives + false_positives) , 2 )
        else:
            precision = None
        
        if true_positives + false_negatives > 0:
            recall = round( true_positives_right_correction / (true_positives + false_negatives) , 2 )
        else:
            recall = None
        
        if precision and recall and precision + recall > 0:
            harmonic_mean = round( 2 * ((precision * recall) / (precision + recall)) , 2 )
        else:
            harmonic_mean = None
                
        if true_positives + false_negatives > 0:
            true_positive_rate = round( true_positives_right_correction / (true_positives + false_negatives) , 2 )
        else:
            true_positive_rate = None
        
        if false_positives + true_negatives > 0:
            false_positive_rate = round( false_positives / (false_positives + true_negatives) , 2 )
        else:
            false_positive_rate = None
    else:
        accuracy = None
        precision = None
        recall = None
        harmonic_mean = None
        true_positive_rate = None
        false_positive_rate = None

    return true_positives_wrong_correction, true_positives_wrong_correction, true_negatives,\
            false_positives, false_negatives, accuracy, precision, recall, harmonic_mean,\
            true_positive_rate, false_positive_rate, duration


if __name__ == "__main__":
    
    # Ler texto correto
    print('-- Leitura do texto correto --', file=sys.stderr)
    original_text = ''.join([line for line in fileinput.input(sys.argv[1:])])
    original_tokens = regex.findall(r'\w+|\s+|\p{P}+', original_text, flags=regex.UNICODE)
    
    print('-- Inserção de erros no texto original (5x) --', file=sys.stderr)
    wrong_texts = get_wrong_texts(5, original_tokens)

    # Gerar estrutura da tabela output
    table = PrettyTable()
    table.field_names = ["Medidas", "Manual", "Aspell", "Hunspell", "Symspelly"]
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

    tpw, tpr, tn, fp, fn, accuracy, precision, recall, hm, tp_rate, fp_rate, d = \
        run_tests('Manual', spellcorrector.correct_text, original_tokens, wrong_texts, 5)
    tpw_list.append(tpw)
    tpr_list.append(tpr)
    tn_list.append(tn)
    fp_list.append(fp)
    fn_list.append(fn)
    accuracy_list.append(accuracy)
    precision_list.append(precision)
    recall_list.append(recall)
    hm_list.append(hm)
    tp_rate_list.append(tp_rate)
    fp_rate_list.append(fp_rate)
    d_list.append(f'{round(d[0],2)} + {round(d[1],2)}')

    function_names = ["Aspell", "Hunspell", "Symspelly"]
    functions = [spellcorrector.correct_line_aspell, spellcorrector.correct_line_hunspell, spellcorrector.correct_line_symspelly]
    for i in range(0,3):
        tpw, tpr, tn, fp, fn, accuracy, precision, recall, hm, tp_rate, fp_rate, d = \
            run_tests(function_names[i], functions[i], original_tokens, wrong_texts, 5)
        tpw_list.append(tpw)
        tpr_list.append(tpr)
        tn_list.append(tn)
        fp_list.append(fp)
        fn_list.append(fn)
        accuracy_list.append(accuracy)
        precision_list.append(precision)
        recall_list.append(recall)
        hm_list.append(hm)
        tp_rate_list.append(tp_rate)
        fp_rate_list.append(fp_rate)
        d_list.append(str(round(d,2)))

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