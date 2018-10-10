#!/usr/bin/python3

import re
import regex
import sys
import getopt


# Processar argumentos do comando
def processArgs():
    inputfile = ''
    outputfile = ''

    # Processa-se opções/argumentos do comando utilizado
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
    fout = sys.stdout if not outputfile else open(outputfile, 'w')

    return fin, fout


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


# Main
def main ():
    # Processamento de argumentos do comando utilizado
    fin, fout = processArgs()  

    # Definição dos elementos químicos
    chemical_symbols = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'Ba', 'Bo', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'Ca', 'Cd', 'C', 'Ce', 'Cf', 'Cl', 'Cn', 'Cm', 'Co', 'Cr', 'Cs', 'Cu', 'Ds', 'Db', 'Dy', 'Er', 'Es', 'Eu', 'Fm', 'Fl', 'F', 'Fe', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hg', 'Hf', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lv', 'Lu', 'Md', 'Mg', 'Mn', 'Mt', 'Mo', 'Mc', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'Nh', 'No', 'Np', 'O', 'Og', 'Os', 'Pb', 'P', 'Pa', 'Pd', 'Po', 'Pr', 'Pm', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Sm', 'Sg', 'Se', 'Si', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ts', 'Tl', 'Ti', 'Tm', 'W', 'U', 'V', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']
    
    # Definição da expressão regular a fazer match
    pattern = r'^(' + '|'.join(chemical_symbols) + ')+$'

    # Processar input com uma palavra por linha e gerar output dos matches
    for line in fin:
        word = line.rstrip()
        word_no_acc = clean_accents(word)
        if re.search(pattern, word_no_acc, re.IGNORECASE):
            composition = regex.match(pattern, word_no_acc, flags=regex.IGNORECASE).captures(1)
            composition = list(map(lambda s: getElement(s, chemical_symbols), composition))
            fout.write(word + ": " + " + ".join(composition) + "\n")

    # Fechar ficheiros abertos
    fin.close()
    fout.close()

main()