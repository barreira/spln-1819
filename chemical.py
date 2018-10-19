#!/usr/bin/python3

"""Find which words can be written as a sequence of chemical symbols.

It receives as input a list of words (one word per line) and generates as output the words that can be
written as a sequence of chemical symbols, as well as the various possible matches (only first if -a
option not inserted).
"""

import re
import regex
import sys
import getopt

# Processar argumentos do comando
def processArgs():
    inputfile = ''
    outputfile = ''
    allMatches = False

    # Processar opções/argumentos do comando utilizado
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"i:o:hva",["ifile=","ofile=","help","version","all"])
    except getopt.GetoptError:
        print('chemical [-a] [-i <inputfile>] [-o <outputfile>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('chemical [-a] [-i <inputfile>] [-o <outputfile>]')
            sys.exit()
        elif opt in ('-v', '--version'):
            print('Version 1.0')
            sys.exit()
        elif opt in ("-a", "--all"):
            allMatches = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    # Definir input e output
    fin = sys.stdin if not inputfile else open(inputfile, 'r')
    fout = sys.stdout if not outputfile else open(outputfile, 'w')

    return fin, fout, allMatches


# Remover acentos de uma palavra
def clean_accents(word):
    word = re.sub(r'[áàãâ]', r'a', word)
    word = re.sub(r'[ÁÀÃÂ]', r'A', word)
    word = re.sub(r'[éèê]', r'e', word)
    word = re.sub(r'[ÉÈÊ]', r'E', word)
    word = re.sub(r'[íìî]', r'i', word)
    word = re.sub(r'[ÍÌÎ]', r'I', word)
    word = re.sub(r'[óòõô]', r'o', word)
    word = re.sub(r'[ÓÒÕÔ]', r'O', word)
    word = re.sub(r'[úùû]', r'u', word)
    word = re.sub(r'[ÚÙÛ]', r'U', word)
    return word


# Obter o elemento correspondente a um símbolo encontrado (sensitive case)
def getElement(s, symbols):
    for symb in symbols:
        if s.lower() == symb.lower():
            return symb
    return s


# Obter a expressão regular que seleciona palavras que apenas são formadas com símbolos químicos, excluindo
# alguns em determinadas posições, indicados no dicionário passado como patâmetro
def builtPattern(chemical_symbols, to_remove):
    # Definição do início do resultado e padrão normal (com todos os elementos químicos)
    r = r'^'
    usualPattern = '|'.join(chemical_symbols)
    currentIndex = 0

    # Percorrer todos os pares (índice, elementos) a remover, ordenados por índice
    for index, elems in sorted(to_remove.items()):
        # Se índice com elementos a remover for superior ao atual, preenche-se o espaço intermédio com
        # o padrão normal
        if currentIndex < index:
            r += r'(?P<elem>' + usualPattern + r'){' + str(index-currentIndex) + r'}'
        # Indica-se elementos a considerar na posição index
        r += r'(?P<elem>' + '|'.join([e for e in chemical_symbols if e not in elems]) + r')'
        # Atualiza-se a variável do índice atual
        currentIndex = index + 1
    
    # Se resultado já tem algum elemento químico, repete-se o padrão normal 0 ou mais vezes
    if currentIndex > 0:
        r += r'(?P<elem>' + usualPattern + r')*$'
    # Se resultado não tem nenhum elemento químico, repete-se o padrão normal 1 ou mais vezes
    else:
        r += r'(?P<elem>' + usualPattern + r')+$'

    return r


# Obter (todas) as combinações possíveis de símbolos químicos, para a formação da palavra indicada
def getMatches(word, allMatches, chemical_symbols, precedents = {}):
    # Inicializar resultado e expressão regular a utilizar
    r = set()
    pattern = builtPattern(chemical_symbols, precedents)
    # Procurar match com o padrão indicado na palavra fornecida
    match = regex.match(pattern, word, flags=regex.IGNORECASE)

    if match:
        # Obter elementos químicos que compõem a palavra, ordenados, e adicioná-los ao resultado
        composition = list(map(lambda s: getElement(s, chemical_symbols), match.captures(1)))
        r.add(tuple(composition))
        if allMatches:
            # Para cada elemento da composição da palavra, procura-se matches alternativos sem esse elemento
            # nessa posição
            for index, elem in enumerate(composition):
                prec = precedents.copy()
                if index in prec:
                    prec[index].append(elem)
                else:
                    prec[index] = [elem]
                r.update(getMatches(word, allMatches, chemical_symbols, prec))

    return r


# Main
def main ():
    # Processamento de argumentos do comando utilizado
    fin, fout, allMatches = processArgs()  

    # Definição dos elementos químicos
    chemical_symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
    
    # Definição da expressão regular a fazer match
    pattern = r'^(' + '|'.join(chemical_symbols) + ')+$'

    content = fin.readlines()
    current_word = 0
    total_words = len(content)
    # Processar input com uma palavra por linha e gerar output dos matches
    for line in content:
        print('Processed ' + str(current_word) + '/' + str(total_words), file=sys.stderr, end='\r')
        word = line.rstrip()
        word_no_acc = clean_accents(word)
        if re.search(pattern, word_no_acc, re.IGNORECASE):
            compositions = getMatches(word_no_acc, allMatches, chemical_symbols)
            fout.write(word + ": " + " | ".join(["+".join(c) for c in compositions]) + "\n")
        current_word += 1

    # Fechar ficheiros abertos
    fin.close()
    fout.close()

main()

