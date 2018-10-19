#!/usr/bin/python3

"""Find which words can be written as a sequence of chemical symbols and generates a chart with the number of occurrences of each chemical element.

It receives as input a list of words (one word per line) and generates as output an image consisting of
a chart with the number of occurrences of each chemical element.
"""

import re
import regex
import sys
import getopt
from collections import Counter, OrderedDict
import numpy as np
import matplotlib.pyplot as plt

# Processar argumentos do comando
def processArgs():
    inputfile = ''
    outputfile = ''

    # Processar opções/argumentos do comando utilizado
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"i:o:hv",["ifile=","ofile=","help","version"])
    except getopt.GetoptError:
        print('chemical [-i <inputfile>] [-o <outputfile>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('chemical [-i <inputfile>] [-o <outputfile>]')
            sys.exit()
        elif opt in ('-v', '--version'):
            print('Version 1.0')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    # Definir input e output
    fin = sys.stdin if not inputfile else open(inputfile, 'r')
    if not outputfile:
        outputfile = 'imagem.svg'

    return fin, outputfile


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


# Desenhar gráfico de barras e guardá-lo como imagem
def drawPlot(c, outfile):
    # Obtenção das abcissas e ordenadas
    labels, values = zip(*c.items())
    n = len(labels)

    # Obtenção da posição dos elementos químicos (ordenadas) no gráfico
    indexes = np.arange(n)
    
    # Definição da largura das barras
    width = 1

    # Definição do tamanho da imagem
    plt.figure(figsize=(n*0.1,n*0.25))

    # Desenhar gráfico de barras horizontal e etiquetas dos elementos químicos
    plt.barh(indexes, values, width)
    plt.yticks(indexes, labels)

    # Inserir nº de ocorrências em cada barra
    for i, v in enumerate(values):
        plt.text(v + n * 0.01, i - 0.2, str(v), color='blue')

    # Guardar figura obtida
    plt.savefig(outfile)


# Main
def main ():
    # Processamento de argumentos do comando utilizado
    fin, outfile = processArgs()  

    # Definir elementos químicos e expressão regular
    chemical_symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
    pattern = r'^(' + '|'.join(chemical_symbols) + r')+$'
    c = Counter()

    # Obter todas as matches das palavras fornecidas e contabilizar nº de ocorrências dos elementos químicos
    for line in fin:
        word = line.rstrip().split('\t')[-1]
        word_no_acc = clean_accents(word).lower()
        if re.search(pattern, word_no_acc, re.IGNORECASE):
            composition = regex.match(pattern, word_no_acc, flags=regex.IGNORECASE).captures(1)
            for elem in composition:
                c[elem] += 1

    # Ordenar as ocorrências dos elementos químicos de forma decrescente
    c = OrderedDict(reversed(c.most_common()))

    # Desenhar gráfico de barras em imagem
    drawPlot(c, outfile)

    # Fechar ficheiro de input
    fin.close()

main()