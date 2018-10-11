import re
import regex
import sys
import getopt
from collections import Counter, OrderedDict
import numpy as np
import matplotlib.pyplot as plt

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

def main ():
    inputfile = ''
    outputfile = ''
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"i:o:hv",["ifile=","ofile=","help=","version="])
    except getopt.GetoptError:
        print('chemical [-i <inputfile>] [-o <outputfile>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('chemical [-i <inputfile>] [-o <outputfile>]')
            sys.exit()
        elif opt == '-v':
            print('Version 1.0')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    chemical_symbols = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'Ba', 'Bo', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'Ca', 'Cd', 'C', 'Ce', 'Cf', 'Cl', 'Cn', 'Cm', 'Co', 'Cr', 'Cs', 'Cu', 'Ds', 'Db', 'Dy', 'Er', 'Es', 'Eu', 'Fm', 'Fl', 'F', 'Fe', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hg', 'Hf', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lv', 'Lu', 'Md', 'Mg', 'Mn', 'Mt', 'Mo', 'Mc', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'Nh', 'No', 'Np', 'O', 'Og', 'Os', 'Pb', 'P', 'Pa', 'Pd', 'Po', 'Pr', 'Pm', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Sm', 'Sg', 'Se', 'Si', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ts', 'Tl', 'Ti', 'Tm', 'W', 'U', 'V', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

    if not inputfile:
        fin = sys.stdin
    else:
        fin = open(inputfile, 'r')

    if not outputfile:
        fout = sys.stdout
    else:
        fout = open(outputfile, 'w')
        
    pattern = r'^(' + '|'.join(chemical_symbols) + ')+$'
    c = Counter()

    for line in fin:
        word = line.rstrip().split('\t')[-1]
        word_no_acc = clean_accents(word).lower()
        if re.search(pattern, word_no_acc, re.IGNORECASE):
            composition = regex.match(pattern, word_no_acc, flags=regex.IGNORECASE).captures(1)
            for elem in composition:
                c[elem] += 1

    # print(c)

    c = OrderedDict(reversed(c.most_common()))

    labels, values = zip(*c.items())

    indexes = np.arange(len(labels))
    width = 1

    plt.figure(figsize=(10,50))

    plt.barh(indexes, values, width)
    plt.yticks(indexes, labels)

    for i, v in enumerate(values):
        plt.text(v + 5, i, str(v), color='blue')

    plt.savefig('figura.svg')

    fin.close()
    fout.close()

main()