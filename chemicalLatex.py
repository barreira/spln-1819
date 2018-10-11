#!/usr/bin/python3

import re
import regex
import sys
import os.path
import getopt
import pubchempy as pcp
from itertools import groupby
from printChemLatex import *


# Processar argumentos do comando
def processArgs():
    inputfile = ''
    outputfile = ''
    partial = True
    formulas = True

    # Processa-se opções/argumentos do comando utilizado
    try: 
        opts, args = getopt.getopt(sys.argv[1:],'i:o:hvan',['ifile=','ofile=','help','version','all','noformulas'])
    except getopt.GetoptError:
        print('Chemical Latex Generator\n' +
              'Usage:\n\tchemicalLatex [-a] [-n] [-i <inputfile>] [-o <outputfile>]\n' +
              'Options:\n\t-a | --all\t\tProcess all words that match, ignoring letter case and accents\n\t-n | --noformulas\tDoesn\'t match formulas, nor does it show its information\n\t-i | --ifile\t\tUsed to indicate input file\n\t-o | --ofile\t\tUsed to indicate output file')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Chemical Latex Generator\n' +
                  'Usage:\n\tchemicalLatex [-a] [-n] [-i <inputfile>] [-o <outputfile>]\n' +
                  'Options:\n\t-a | --all\t\tProcess all words that match, ignoring letter case and accents\n\t-n | --noformulas\tDoesn\'t match formulas, nor does it show its information\n\t-i | --ifile\t\tUsed to indicate input file\n\t-o | --ofile\t\tUsed to indicate output file')
            sys.exit()
        elif opt in ('-v', '--version'):
            print('Version 1.0')
            sys.exit()
        elif opt in ('-a', '--all'):
            partial = False
        elif opt in ('-n', '--noformulas'):
            formulas = False
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg

    # Definir input e output
    fin = sys.stdin if not inputfile else open(inputfile, 'r')

    if not outputfile:
        fout = sys.stdout
        outputdir = '.' 
    else:
        fout = open(outputfile, 'w')
        if '/' in outputfile:
            outputdir = outputfile.rpartition('/')[0]
        else:
            outputdir = '.'

    # Definir path para a pasta dos resources
    if os.path.isfile(outputdir + "/resources/periodic_table.info") \
                and os.path.isfile(outputdir + "/resources/Front.jpg"):
        resourcespath = outputdir + "/resources"
    elif os.path.isfile("/usr/local/bin/resources/periodic_table.info") \
                and os.path.isfile("/usr/local/bin/resources/Front.jpg"):
        resourcespath = "/usr/local/bin/resources"
    else:
        print('Chemical Latex Generator\n' +
                  'Error: No file \'Resources\' found')
        sys.exit(3)

    return fin, fout, resourcespath, partial, formulas


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


# Obter um atributo dum elemento químico que é especificado como texto, com uma estrutura específica 
def getElemAttribute(element, attribute):
    l = re.findall(attribute + r': (.+)\n', element)
    if len(l)==0: r = None
    else: r = l[0]
    return r


# Obter a informação da tabela periódica e respetivos elementos químicos a partir de um ficheiro, cujo
# conteúdo deve seguir uma estrutura específica
def getPeriodicTableInfo(filename):
    fd = open(filename)
    content = fd.read()
    fd.close()

    periodic_table = {}
    info = re.findall(r'\{([^}]*)\}', content)

    for element in info:
        symbol = getElemAttribute(element, 'symbol')
        periodic_table[symbol.lower()] = {
            'name': getElemAttribute(element, 'name'),
            'appearance': getElemAttribute(element, 'appearance'),
            'mass': getElemAttribute(element, 'atomic_mass'),
            'category': getElemAttribute(element, 'category'),
            'density': getElemAttribute(element, 'density'),
            'number': getElemAttribute(element, 'number'),
            'period': getElemAttribute(element, 'period'),
            'phase': getElemAttribute(element, 'phase'),
            'spectral_img': getElemAttribute(element, 'spectral_img'),
            'summary': getElemAttribute(element, 'summary'),
            'symbol': symbol,
            'xpos': getElemAttribute(element, 'xpos'),
            'ypos': getElemAttribute(element, 'ypos'),
            'relative_position': getElemAttribute(element, 'relative_position'),
            'occurrences': 0
        }
        if not periodic_table[symbol.lower()]['relative_position']:
            periodic_table[symbol.lower()]['relative_position'] = ''
        else:
            periodic_table[symbol.lower()]['relative_position'] += ', '

    return dict(sorted(periodic_table.items(), key = lambda e: float(e[1]['number'])))


# Pesquisar fórmula no pubchem e obter respetivas informações
def searchFormulaInfo(formula):
    info = ''
    cids = set(pcp.get_cids(formula, 'name')).intersection(pcp.get_cids(formula, 'formula'))

    for cid in cids:
        c = pcp.Compound.from_cid(cid)
        name = c.iupac_name
        altNames = c.synonyms[:4]

        if not name and len(altNames) > 0:
            name = altNames[0]
        if name in altNames:
            altNames.remove(name)

        if name: 
            info += 'This formula has the IUPAC name \\textbf{' + name + '}'
            if c.molecular_formula: info += ' and the molecular formula \\textbf{' + c.molecular_formula + '}'
            info += '. '
        if len(altNames) > 1:
            info +=  'Some alternative names are ' + ', '.join(str(n) for n in altNames[:-1]) + ' and ' + altNames[-1] + '. '
        elif len(altNames) == 1:
            info +=  'An alternative name is ' + altNames[0] + '. '
        if c.complexity: info += 'Its complexity has value ' + str(c.complexity) + '. '
        if c.exact_mass: info += 'The exact mass is ' + str(c.exact_mass) + '. '
        if c.molecular_weight: info += 'The molecular weight is ' + str(c.molecular_weight) + '. '
        if c.monoisotopic_mass: info += 'The monoisotopic mass is ' + str(c.monoisotopic_mass) + '. '

    return info


# Pocessar palavra de forma a escrever, caso seja uma composição de elementos químicos, informação sobre esses 
# elementos e/ou, caso seja uma fórmula, informação sobre a mesma
def processWord(word, partial, formulas, patternElements, patternFormulas, ptable,
                                            formulas_found, formulas_not_found, fout):
    
    word = clean_accents(word).lower() if not partial else word

    # Escrever sobre elementos químicos encontrados
    if re.search(patternElements, word, re.IGNORECASE if not partial else 0):
        composition = regex.match(patternElements, word, flags=regex.IGNORECASE if not partial else 0).captures(1)
        for symbol in composition:
            ptable[symbol.lower()]['occurrences'] += 1
        printChemElements(fout, composition, ptable)
    else:
        fout.write(word.replace('_','\_').replace('\n','\n\n'))

    # Escrever sobre fórmulas químicas encontradas
    if formulas and re.search(patternFormulas, word, re.IGNORECASE if not partial else 0):
        composition = regex.match(patternFormulas, word, flags=regex.IGNORECASE if not partial else 0).captures(1)
        composition = list(map(lambda e: ptable[e.lower()]['symbol'] if e.lower() in ptable else e , composition))
        formula = ''.join([key + str(len(list(group))) for key, group in groupby(composition)]).replace('1','')
        if formula:
            # Se fórmula ainda não foi pesquisada, efetua-se a pesquisa e, caso se encontre, apresenta-se informações
            if not (formula in formulas_found or formula in formulas_not_found):
                # Pesquisa-se fórmula
                try:
                    info = searchFormulaInfo(formula)
                except pcp.PubChemHTTPError:
                    info = ''

                # Se se obteve informação, apresenta-se-a numa nota de rodapé e junta-se a fórmula às encontradas
                if info:
                    printFoot(fout, 'label', formula, info)
                    formulas_found[formula] = 1
                # Se não se obteve informação, junta-se fórmula às não encontradas
                else:
                    formulas_not_found.append(formula)

            # Se fórmula já foi pesquisada e encontrada, apenas se insere referência para a nota de rodapé já criada
            elif formula in formulas_found:
                printFoot(fout, 'ref', formula)
                formulas_found[formula] += 1;


# Main
def main():
    # Processamento de argumentos do comando utilizado
    fin, fout, resourcespath, partial, formulas = processArgs()

    # Leitura da informação da tabela periódica e inicialização de variáveis (padrões, conteúdo do input, ...)
    periodic_table = getPeriodicTableInfo(resourcespath + '/periodic_table.info')
    chemical_symbols = list(map(lambda e: e['symbol'], periodic_table.values()))
    patternElements = r'^(' + '|'.join(chemical_symbols) + ')+$'
    patternFormulas = r'^(' + '|'.join(chemical_symbols + [r'\d']) + ')+$'
    formulas_found = {}
    formulas_not_found = []
    content = re.findall(r'\w+|\W+', fin.read())
    total_parts = len(content)
    current_part = 0

    # Escreve-se início do documento
    printInitDocument(fout, resourcespath)

    # Processa-se o texto de input e escreve-se o output
    for word in content:
        # Imprime-se nº de partes processadas no total
        print('Processed ' + str(current_part) + '/' + str(total_parts), end='\r')

        # Processa-se palavra
        processWord(word, partial, formulas, patternElements, patternFormulas, 
                    periodic_table, formulas_found, formulas_not_found, fout)

        # Incrementa-se o nº de partes processadas
        current_part += 1

    # Escreve-se fim do documento
    printEndDocument(fout, resourcespath, periodic_table, formulas_found)

    # Fechar ficheiros abertos
    fin.close()
    fout.close()

main()
