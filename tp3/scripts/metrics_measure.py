import sys
import time
import regex
import string
import fileinput
import numpy as np
import spellcorrector_tags

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


def main():
    # Ler texto correto
    print('-- Leitura do texto correto --', file=sys.stderr)
    original_text = ''.join([line for line in fileinput.input(sys.argv[1:])])
    original_tokens = regex.findall(r'\w+|\s+|\p{P}+', original_text, flags=regex.UNICODE)

    # Gerar texto com erros
    print('-- Inserção de erros no texto --', file=sys.stderr)
    errors_text = gen_text_with_errors(original_tokens)
    errors_tokens = regex.findall(r'\w+|\s+|\p{P}+', errors_text, flags=regex.UNICODE)
    with open('errors.txt', 'w+') as fd:
        print(errors_text, file=fd)

    # Corrigir erros do texto
    print('-- Correção dos erros do texto --', file=sys.stderr)
    t1 = time.time()
    pos_freq, words_freq = spellcorrector_tags.analyze_large_text()
    t2 = time.time()
    corrected_text = spellcorrector_tags.correct_text(pos_freq, words_freq, text_lines=errors_text.split('\n'))
    t3 = time.time()
    corrected_tokens = regex.findall(r'\w+|\s+|\p{P}+', corrected_text, flags=regex.UNICODE)
    with open('corrected.txt', 'w+') as fd:
        print(corrected_text, file=fd)

    print('Load Time:\t\t', round(t2-t1,2), 'sec')
    print('Correction Time:\t', round(t3-t2,2), 'sec\n')

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
    
    true_positives = true_positives_right_correction + true_positives_wrong_correction
    
    print('True Positives Wrong:\t', true_positives_wrong_correction)
    print('True Positives Right:\t', true_positives_right_correction)
    print('True Negatives:\t\t', true_negatives)
    print('False Positives:\t', false_positives)
    print('False Negatives:\t', false_negatives)
    
    print()

    if total_words > 0:
        accuracy = (true_positives_right_correction + true_negatives) / total_words
        print('Accuracy:\t', round(accuracy,2))

        if true_positives + false_positives > 0:
            precision = true_positives_right_correction / (true_positives + false_positives)
            print('Precision:\t', round(precision,2))
        
        if true_positives + false_negatives > 0:
            recall = true_positives_right_correction / (true_positives + false_negatives)
            print('Recall:\t\t', round(recall,2))
        
        if precision and recall and precision + recall>0:
            harmonic_mean = 2 * ((precision * recall) / (precision + recall))
            print('Harmonic Mean:\t', round(harmonic_mean,2))
        
        if true_positives + false_negatives > 0:
            true_positive_rate = true_positives_right_correction / (true_positives + false_negatives)
            print('TPR:\t\t', round(true_positive_rate,2))

        if false_positives + true_negatives > 0:
            false_positive_rate = false_positives / (false_positives + true_negatives)
            print('FPR:\t\t', round(false_positive_rate,2))

    # TODO: Gerar ROC e medir AUC

if __name__ == "__main__":
    main()