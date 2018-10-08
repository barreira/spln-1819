#!/usr/bin/python3

import re
import regex
import sys
import getopt
import pubchempy as pcp


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

def getElemAttribute(element, attribute):
    l = re.findall(attribute + r': (.+)\n', element)
    if len(l)==0: r = None
    else: r = l[0]
    return r

def elements_ordered():
    return ['h', 'li', 'na', 'k', 'rb', 'cs', 'fr', 'be', 'mg', 'ca', 'sr', 'ba', 'ra', 'sc', 'y', 'ti', 'zr', 'hf', 'rf', 'v', 'nb', 'ta', 'db', 'cr', 'mo', 'w', 'sg', 'mn', 'tc', 're', 'bh', 'fe', 'ru', 'os', 'hs', 'co', 'rh', 'ir', 'mt', 'ni', 'pd', 'pt', 'ds', 'cu', 'ag', 'au', 'rg', 'zn', 'cd', 'hg', 'cn', 'ga', 'al', 'b', 'in', 'tl', 'nh', 'c', 'si', 'ge', 'sn', 'pb', 'fl', 'n', 'p', 'as', 'sb', 'bi', 'mc', 'o', 's', 'se', 'te', 'po', 'lv', 'f', 'cl', 'br', 'i', 'at', 'ts', 'ne', 'he', 'ar', 'kr', 'xe', 'rn', 'og', 'la', 'ac', 'ce', 'th', 'pr', 'pa', 'nd', 'u', 'pm', 'np', 'sm', 'pu', 'eu', 'am', 'gd', 'cm', 'tb', 'bk', 'dy', 'cf', 'ho', 'es', 'er', 'fm', 'tm', 'md', 'yb', 'no', 'lu', 'lr']

def printInitDocument(fout):
    fout.write("\\documentclass{article}\n" +
                "\\usepackage[utf8]{inputenc}\n" +
                "\\usepackage{tikz}\n" +
                "\\usepackage[paper=portrait,pagesize]{typearea}\n" +
                "\\usepackage{tabularx}\n" +
                "\\usepackage{eso-pic}\n" +
                "\\usepackage{xcolor}\n" +
                "\\usepackage[margin=4cm]{geometry}\n"+
                "\\usepackage[hidelinks]{hyperref}\n" +
                "\\usepackage[toc,page]{appendix}\n" +
                "\\usetikzlibrary{shapes,calc}\n\n" +
                "%% Define Boxes of Elements  \n\\newcommand{\\CommonElementTextFormat}[4]\n{\n  \\begin{minipage}{2.2cm}\n    \\centering\n      {\\textbf{#1} \\hfill #2}%\n      \\linebreak \\linebreak\n      {\\textbf{#3}}%\n      \\linebreak \\linebreak\n      {{#4}}\n  \\end{minipage}\n}\n\n" +
                "\\newcommand{\\NaturalElementTextFormat}[4]\n{\n  \\CommonElementTextFormat{#1}{#2}{\\LARGE {#3}}{#4}\n}\n\n\n" +
                "%% Define 'footlabel'\n\\newcommand{\\footlabel}[2]{%\n    \\addtocounter{footnote}{1}%\n    \\footnotetext[\\thefootnote]{%\n        \\addtocounter{footnote}{-1}%\n        \\refstepcounter{footnote}\\label{#1}%\n        #2%\n    }%\n    $^{\\ref{#1}}$%\n}\n\n\\newcommand{\\footref}[1]{%\n    $^{\\ref{#1}}$%\n}\n" +
                "%% Fill Color Styles\n\\tikzstyle{AlkaliMetalFill} = [fill=blue!55]\n\\tikzstyle{AlkalineEarthMetalFill} = [fill=blue!40]\n\\tikzstyle{TransitionMetalFill} = [fill=blue!25]\n\\tikzstyle{PostTransitionMetalFill} = [fill=orange!25]\n\\tikzstyle{MetalloidFill} = [fill=yellow!15]\n\\tikzstyle{NonmetalFill} = [fill=green!25]\n\\tikzstyle{HalogenFill} = [fill=green!40]\n\\tikzstyle{NobleGasFill} = [fill=green!55]\n\\tikzstyle{LanthanideFill} = [fill=purple!50]\n\\tikzstyle{ActinideFill} = [fill=purple!25]\n\\tikzstyle{UnknownFill} = [fill=gray!25]\n\n" +
                "%% Element Styles\n\\tikzstyle{AlkaliMetal} = [draw=black, AlkaliMetalFill, minimum width=2.75cm, minimum height=2.75cm, node distance=2.75cm]\n\\tikzstyle{AlkalineEarthMetal} = [AlkaliMetal, AlkalineEarthMetalFill]\n\\tikzstyle{TransitionMetal} = [AlkaliMetal, TransitionMetalFill]\n\\tikzstyle{PostTransitionMetal} = [AlkaliMetal, PostTransitionMetalFill]\n\\tikzstyle{Metalloid} = [AlkaliMetal, MetalloidFill]\n\\tikzstyle{Nonmetal} = [AlkaliMetal, NonmetalFill]\n\\tikzstyle{Halogen} = [AlkaliMetal, HalogenFill]\n\\tikzstyle{NobleGas} = [AlkaliMetal, NobleGasFill]\n\\tikzstyle{Lanthanide} = [AlkaliMetal, LanthanideFill]\n\\tikzstyle{Actinide} = [AlkaliMetal, ActinideFill]\n\\tikzstyle{Unknown} = [AlkaliMetal, UnknownFill]\n\\tikzstyle{PeriodLabel} = [font={\\sffamily\\LARGE}, node distance=2.0cm]\n\\tikzstyle{GroupLabel} = [font={\\sffamily\\LARGE}, minimum width=2.75cm, node distance=2.0cm]\n\\tikzstyle{TitleLabel} = [font={\\sffamily\\Huge\\bfseries}]\n\n" +
                "%% Center Boxes According to Text\n\\newbox\\mybox\n\\def\\centerfigure#1{%\n  \\setbox\\mybox\\hbox{#1}%\n  \\raisebox{-0.43\\dimexpr\\ht\\mybox+\\dp\\mybox}{\\copy\\mybox}%\n}\n\n" +
                "\\begin{document}\n\n" +
                "%% Cover Page\n\\begingroup\n\\thispagestyle{empty}\n\\AddToShipoutPicture*{\\put(0,0){\\includegraphics[scale=1.76]{resources/Front}}}\n\\centering {\n    \\vspace*{-0.01cm}\n    \\Huge\\sffamily\\selectfont\\textcolor{white}{\\textbf{Chemical Elements}}\\par\n    \\vspace*{0.5cm}\n    \n    \\LARGE\\textcolor{white}{Obtaining chemical elements that constitute everyday words}\\par\n    \\vspace*{8.6cm}\n}\n\n\\hfill\n\\begin{minipage}{0.3\\textwidth}\n    \\centering\\LARGE\\sffamily\\selectfont {\n        \\textcolor{white}{João Barreira}\n        \n        \\vspace{0.3cm}\n        \n        \\textcolor{white}{Mafalda Nunes}\n    }\\par\n\\end{minipage}\n\n\\vspace{5.2cm}\n\n\n{\\Large\\par\\sffamily\\selectfont\\hfill \\textcolor{white}{Scripting e Processamento de Linguagem Natural}}\n\n\\endgroup\n\\newpage\n\n" +
                "%% Obtained Text\n\\section{Obtained Text}\n\n"
            )

def printEndDocument(fout, ptable):
    # Apendices
    fout.write("\n\\setcounter{section}{0}\n" +
                "\\setcounter{subsection}{0}\n\n" +
                # Página horizontal para a TP
                "\\newpage\n" +
                "\\KOMAoptions{paper=landscape,pagesize}\n" +
                "\\recalctypearea\n\n" +
                # Apêndices
                "%% Appendices\n" +
                "\\appendixpage\n" +
                "\\renewcommand{\\thesubsection}{\\Alph{subsection}}\n\n")

    # Tabela periódica
    fout.write("%%Periodic Table\n" +
                "\\setlength{\\extrarowheight}{0.95\\textheight}\n\n" +
                "\\subsection{Periodic Table of Chemical Elements}\n" +
                "\\label{anexo:periodic_table}\n\n" +
                "\\noindent\\makebox[\\textwidth]{\n" +
                "    \\begin{tabularx}{1.25\\textwidth}{c}\n" +
                "        \\begin{tikzpicture}[font=\\sffamily, scale=0.45, transform shape]\n\n")

    for symbol in elements_ordered():
        e = ptable[symbol]
        ############################# Hiperligação não está a funcionar
        fout.write("            \\hyperlink{subsubsection::" + e['symbol'] + "}{\\node[name=" + e['symbol']+ ", " + e['relative_position'] + e['category'] + "] {\\NaturalElementTextFormat{" + e['number'] + "}{" + str(round(float(e['mass']),3)) + "}{" + e['symbol'] + "}{" + e['name'] + "}};}\n")
    
    fout.write("\n            \\node[name=LaLu, below of=Y, Lanthanide] {\\NaturalElementTextFormat{57-71}{}{La-Lu}{Lanthanide}};\n" +
                "            \\node[name=AcLr, below of=LaLu, Actinide] {\\NaturalElementTextFormat{89-103}{}{Ac-Lr}{Actinide}};\n" +
                "        %% Period\n            \\node[name=Period1, left of=H, PeriodLabel] {1};\n            \\node[name=Period2, left of=Li, PeriodLabel] {2};\n            \\node[name=Period3, left of=Na, PeriodLabel] {3}; \n            \\node[name=Period4, left of=K, PeriodLabel] {4}; \n            \\node[name=Period5, left of=Rb, PeriodLabel] {5};\n            \\node[name=Period6, left of=Cs, PeriodLabel] {6};\n            \\node[name=Period7, left of=Fr, PeriodLabel] {7};\n\n" +
                "        %% Group\n            \\node[name=Group1, above of=H, GroupLabel] {1 \\hfill IA};\n            \\node[name=Group2, above of=Be, GroupLabel] {2 \\hfill IIA};\n            \\node[name=Group3, above of=Sc, GroupLabel] {3 \\hfill IIIA};\n            \\node[name=Group4, above of=Ti, GroupLabel] {4 \\hfill IVB};\n            \\node[name=Group5, above of=V, GroupLabel] {5 \\hfill VB};\n            \\node[name=Group6, above of=Cr, GroupLabel] {6 \\hfill VIB};\n            \\node[name=Group7, above of=Mn, GroupLabel] {7 \\hfill VIIB};\n            \\node[name=Group8, above of=Fe, GroupLabel] {8 \\hfill VIIIB};\n            \\node[name=Group9, above of=Co, GroupLabel] {9 \\hfill VIIIB};\n            \\node[name=Group10, above of=Ni, GroupLabel] {10 \\hfill VIIIB};\n            \\node[name=Group11, above of=Cu, GroupLabel] {11 \\hfill IB};\n            \\node[name=Group12, above of=Zn, GroupLabel] {12 \\hfill IIB};\n            \\node[name=Group13, above of=B, GroupLabel] {13 \\hfill IIIA};\n            \\node[name=Group14, above of=C, GroupLabel] {14 \\hfill IVA};\n            \\node[name=Group15, above of=N, GroupLabel] {15 \\hfill VA};\n            \\node[name=Group16, above of=O, GroupLabel] {16 \\hfill VIA};\n            \\node[name=Group17, above of=F, GroupLabel] {17 \\hfill VIIA};\n            \\node[name=Group18, above of=He, GroupLabel] {18 \\hfill VIIIA};\n\n" +
                "        %% Draw dotted lines connecting Lanthanide breakout to main table\n            \\draw (LaLu.north west) edge[dotted] (La.north west)\n                        (LaLu.north east) edge[dotted] (Lu.north east)\n                        (LaLu.south west) edge[dotted] (La.south west)\n                        (LaLu.south east) edge[dotted] (Lu.south east);\n" + 
                "        %% Draw dotted lines connecting Actinide breakout to main table\n            \\draw (AcLr.north west) edge[dotted] (Ac.north west)\n                        (AcLr.north east) edge[dotted] (Lr.north east)\n                        (AcLr.south west) edge[dotted] (Ac.south west)\n                        (AcLr.south east) edge[dotted] (Lr.south east);\n\n" +
                "        %% Legend\n            \\draw[black, AlkaliMetalFill] ($(La.north -| Fr.west) + (1em,1.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkali Metal};\n            \\draw[black, AlkalineEarthMetalFill] ($(La.north -| Fr.west) + (1em,-0.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkaline Earth Metal};\n            \\draw[black, TransitionMetalFill] ($(La.north -| Fr.west) + (1em,-2.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Transition Metal};\n            \\draw[black, PostTransitionMetal] ($(La.north -| Fr.west) + (1em,-3.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Post-Transition Metal};\n            \\draw[black, MetalloidFill] ($(La.north -| Fr.west) + (1em,-5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Metalloid};\n            \\draw[black, NonmetalFill] ($(La.north -| Fr.west) + (1em,-6.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Non-metal};\n            \\draw[black, NobleGasFill] ($(La.north -| Fr.west) + (1em,-8.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Noble Gas};\n            \\draw[black, LanthanideFill] ($(La.north -| Fr.west) + (1em,-9.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Lanthanide};\n\n            \\draw[black, ActinideFill] ($(La.north -| Fr.west) + (1em,-11.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Actinide};\n\n            \\draw[black, UnknownFill] ($(La.north -| Fr.west) + (1em,-12.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Unknown};\n\n            \\node at ($(La.north -| Fr.west) + (10em,-18.0em)$) [name=elementLegend, AlkaliMetal, fill=white]\n                {\\NaturalElementTextFormat{Z}{mass}{Symbol}{Name}};\n\n"
                "        \\end{tikzpicture}\n" +
                "    \\end{tabularx}}\n\n" +
                "\\newpage\n" +
                "\\KOMAoptions{paper=portrait,pagesize}\n" +
                "\\recalctypearea\n\n")
    
    # Informação sobre elementos químicos
    fout.write("%% Chemical Elements Information\n" +
                "\\subsection{Chemical Elements Information}\n" +
                "\\label{anexo:elements_info}\n\n")

    for (k,v) in ptable.items():
        fout.write("\\hypertarget{subsubsection::" + v['symbol'] + "}{}\\subsubsection{" + v['name'] + " (" + v['symbol'] + ")}\n\n"
                    "Description: " + v['summary'] + "\n\n")
        if v['spectral_img'] != 'null':
            fout.write("\\immediate\\write18{wget -nc -nd -q -r -P ./resources/spectral_img -A jpeg,jpg,bmp,gif,png " + v['spectral_img'] + "}\n" +
                "\\begin{figure}[!ht]\n    \\centering\n    \\includegraphics[width=12cm]{resources/spectral_img/" + v['spectral_img'].split('/')[-1] + "}\n    \\caption{" + v['name'] + " Spectral Image}\n\\end{figure}\n\n")

    fout.write("\\end{document}\n")

def main ():

    # Definição das opções disponíveis para o comando
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

    # Leitura da informação da tabela periódica
    fd = open("resources/periodic_table.info")
    ftp = fd.read()
    fd.close()

    periodic_table = {}
    content = re.findall(r"\{([^}]*)\}", ftp)

    for element in content:
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
            'relative_position': getElemAttribute(element, 'relative_position')
        }
        if not periodic_table[symbol.lower()]['relative_position']:
            periodic_table[symbol.lower()]['relative_position'] = ''
        else:
            periodic_table[symbol.lower()]['relative_position'] += ', '

    periodic_table = dict(sorted(periodic_table.items(), key = lambda e: float(e[1]['number'])))

    chemical_symbols = list(periodic_table.keys())
    words_found = []
    words_not_found = []
    ########################### chemical_symbols tem o Uue; faltam outros elementos
    # chemical_symbols2 = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'Ba', 'B', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'Ca', 'Cd', 'C', 'Ce', 'Cf', 'Cl', 'Cn', 'Cm', 'Co', 'Cr', 'Cs', 'Cu', 'Ds', 'Db', 'Dy', 'Er', 'Es', 'Eu', 'Fm', 'Fl', 'F', 'Fe', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hg', 'Hf', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lv', 'Lu', 'Md', 'Mg', 'Mn', 'Mt', 'Mo', 'Mc', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'Nh', 'No', 'Np', 'O', 'Og', 'Os', 'Pb', 'P', 'Pa', 'Pd', 'Po', 'Pr', 'Pm', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Sm', 'Sg', 'Se', 'Si', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ts', 'Tl', 'Ti', 'Tm', 'W', 'U', 'V', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

    # Definir input e output
    if not inputfile:
        fin = sys.stdin
    else:
        fin = open(inputfile, 'r')

    if not outputfile:
        fout = sys.stdout
    else:
        fout = open(outputfile, 'w')

    # Processar o texto de input e escrever output
    printInitDocument(fout)

    pattern = r'^(' + '|'.join(chemical_symbols) + ')+$'
    content = re.findall(r'\w+|\W+', fin.read())
    total_parts = len(content)
    current_part = 0

    for word in content:
        print('Processed ' + str(current_part) + '/' + str(total_parts), end='\r')
        word_no_acc = clean_accents(word).lower()
        if re.search(pattern, word_no_acc, re.IGNORECASE):
            composition = regex.match(pattern, word_no_acc, flags=regex.IGNORECASE).captures(1)
            composition = list(map(lambda elem: 
                "\\centerfigure{\\begin{tikzpicture}[font=\\sffamily, scale=0.3, transform shape]\n  \\node[name=" + periodic_table[elem.lower()]['symbol'] + ", " + periodic_table[elem.lower()]['category'] + "] {\\NaturalElementTextFormat{" + periodic_table[elem.lower()]['number'] + "}{" + str(round(float(periodic_table[elem.lower()]['mass']), 3)) + "}{" + periodic_table[elem.lower()]['symbol'] + "}{" + periodic_table[elem.lower()]['name'] + "}};\n\\end{tikzpicture}}", composition))
            fout.write("\n+\n".join(composition))
            if not word_no_acc in words_found + words_not_found:
                info = ''
                try:
                    for cid in pcp.get_cids(word, 'name'):
                        if pcp.Compound.from_cid(cid).iupac_name:
                            info += pcp.Compound.from_cid(cid).iupac_name
                except pcp.PubChemHTTPError:
                    pass
                if info:
                    fout.write(' \\footlabel{' + word_no_acc + '}{' + info + '}\n')
                    words_found.append(word_no_acc)
                else:
                    words_not_found.append(word_no_acc)
            elif word_no_acc in words_found:
                fout.write(' \\footref{' + word_no_acc + '}\n')
        else:
            fout.write(word.replace("_","\_").replace("\n","\n\n"))
        current_part += 1

    printEndDocument(fout, periodic_table)

    fin.close()
    fout.close()

main()