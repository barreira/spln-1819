import math


# Arredondar número para o próximo de base 10
def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


# Imprimir início de documento latex
def printInitDocument(fout, resourcespath):
    fout.write('\\documentclass{article}\n' +
                '\\usepackage[utf8]{inputenc}\n' +
                '\\usepackage{indentfirst}\n'
                '\\usepackage{tikz}\n' +
                '\\usepackage[paper=portrait,pagesize]{typearea}\n' +
                '\\usepackage{tabularx}\n' +
                '\\usepackage{bchart}\n' +
                '\\usepackage{eso-pic}\n' +
                '\\usepackage{xcolor}\n' +
                '\\usepackage[margin=4cm]{geometry}\n'+
                '\\usepackage[hidelinks]{hyperref}\n' +
                '\\usepackage[toc,page]{appendix}\n' +
                '\\usetikzlibrary{shapes,calc}\n\n' +
                '%% Define Boxes of Elements  \n\\newcommand{\\CommonElementTextFormat}[4]\n{\n  \\begin{minipage}{2.2cm}\n    \\centering\n      {\\textbf{#1} \\hfill #2}%\n      \\linebreak \\linebreak\n      {\\textbf{#3}}%\n      \\linebreak \\linebreak\n      {{#4}}\n  \\end{minipage}\n}\n\n' +
                '\\newcommand{\\NaturalElementTextFormat}[4]\n{\n  \\CommonElementTextFormat{#1}{#2}{\\LARGE {#3}}{#4}\n}\n\n\n' +
                '%% Define \'footlabel\'\n\\newcommand{\\footlabel}[2]{%\n    \\addtocounter{footnote}{1}%\n    \\footnotetext[\\thefootnote]{%\n        \\addtocounter{footnote}{-1}%\n        \\refstepcounter{footnote}\\label{#1}%\n        #2%\n    }%\n    $^{\\ref{#1}}$%\n}\n\n\\newcommand{\\footref}[1]{%\n    $^{\\ref{#1}}$%\n}\n\n' +
                '%% Fill Color Styles\n\\tikzstyle{AlkaliMetalFill} = [fill=blue!55]\n\\tikzstyle{AlkalineEarthMetalFill} = [fill=blue!40]\n\\tikzstyle{TransitionMetalFill} = [fill=blue!25]\n\\tikzstyle{PostTransitionMetalFill} = [fill=orange!25]\n\\tikzstyle{MetalloidFill} = [fill=yellow!15]\n\\tikzstyle{NonmetalFill} = [fill=green!25]\n\\tikzstyle{HalogenFill} = [fill=green!40]\n\\tikzstyle{NobleGasFill} = [fill=green!55]\n\\tikzstyle{LanthanideFill} = [fill=purple!50]\n\\tikzstyle{ActinideFill} = [fill=purple!25]\n\\tikzstyle{UnknownFill} = [fill=gray!25]\n\n' +
                '%% Element Styles\n\\tikzstyle{AlkaliMetal} = [draw=black, AlkaliMetalFill, minimum width=2.75cm, minimum height=2.75cm, node distance=2.75cm]\n\\tikzstyle{AlkalineEarthMetal} = [AlkaliMetal, AlkalineEarthMetalFill]\n\\tikzstyle{TransitionMetal} = [AlkaliMetal, TransitionMetalFill]\n\\tikzstyle{PostTransitionMetal} = [AlkaliMetal, PostTransitionMetalFill]\n\\tikzstyle{Metalloid} = [AlkaliMetal, MetalloidFill]\n\\tikzstyle{Nonmetal} = [AlkaliMetal, NonmetalFill]\n\\tikzstyle{Halogen} = [AlkaliMetal, HalogenFill]\n\\tikzstyle{NobleGas} = [AlkaliMetal, NobleGasFill]\n\\tikzstyle{Lanthanide} = [AlkaliMetal, LanthanideFill]\n\\tikzstyle{Actinide} = [AlkaliMetal, ActinideFill]\n\\tikzstyle{Unknown} = [AlkaliMetal, UnknownFill]\n\\tikzstyle{PeriodLabel} = [font={\\sffamily\\LARGE}, node distance=2.0cm]\n\\tikzstyle{GroupLabel} = [font={\\sffamily\\LARGE}, minimum width=2.75cm, node distance=2.0cm]\n\\tikzstyle{TitleLabel} = [font={\\sffamily\\Huge\\bfseries}]\n\n' +
                '%% Center Boxes According to Text\n\\newbox\\mybox\n\\def\\centerfigure#1{%\n  \\setbox\\mybox\\hbox{#1}%\n  \\raisebox{-0.43\\dimexpr\\ht\\mybox+\\dp\\mybox}{\\copy\\mybox}%\n}\n\n' +
                '\\begin{document}\n\n' +
                '\\lineskip = 0.25cm\n\n' +
                '%% Cover Page\n\\begingroup\n\\thispagestyle{empty}\n\\AddToShipoutPicture*{\\put(0,0){\\includegraphics[scale=1.76]{' + resourcespath+ '/Front}}}\n\\centering {\n    \\vspace*{-0.01cm}\n    \\Huge\\sffamily\\selectfont\\textcolor{white}{\\textbf{Chemical Elements}}\\par\n    \\vspace*{0.5cm}\n    \n    \\LARGE\\textcolor{white}{Obtaining chemical elements that constitute everyday words}\\par\n    \\vspace*{8.6cm}\n}\n\n\\hfill\n\\begin{minipage}{0.3\\textwidth}\n    \\centering\\LARGE\\sffamily\\selectfont {\n        \\textcolor{white}{João Barreira}\n        \n        \\vspace{0.3cm}\n        \n        \\textcolor{white}{Mafalda Nunes}\n    }\\par\n\\end{minipage}\n\n\\vspace{5.2cm}\n\n\n{\\Large\\par\\sffamily\\selectfont\\hfill \\textcolor{white}{Scripting e Processamento de Linguagem Natural}}\n\n\\endgroup\n\\newpage\n\n' +
                '%% Obtained Text\n\\section{Obtained Text}\n\n'
            )


# Imprimir nodos representantes de elementos químicos de uma lista
def printChemElements(fout, composition, ptable):
    effected_word = list(map(lambda elem: 
        '\\scalebox{0.3}{\n'
        '  \\centerfigure{\\begin{tikzpicture}[font=\\sffamily, transform shape]\n' + 
        '    \\node[name=' + ptable[elem.lower()]['symbol'] + ', ' + ptable[elem.lower()]['category'] + ', rounded corners=.15cm, node distance=3cm] {\\hyperlink{subsubsection::' + ptable[elem.lower()]['symbol'] + '}{\\NaturalElementTextFormat{' + ptable[elem.lower()]['number'] + '}{' + str(round(float(ptable[elem.lower()]['mass']), 3)) + '}{' + ptable[elem.lower()]['symbol'] + '}{' + ptable[elem.lower()]['name'] + '}}};\n' +
        '  \\end{tikzpicture}}\n' +
        '}', composition))
    fout.write('\n+\n'.join(effected_word))


# Imprimir notas de rodapé
def printFoot(fout, type, formula, info=''):
    if type=='label':
        fout.write('\\footlabel{' + formula + '}{' + info.replace('_','\_').replace('\{','{').replace('\}','}') + '}')
    elif type=='ref':
        fout.write('\\footref{' + formula + '}')


# Imprimir tabela periódica nos apêndices
def printPeriodicTableApp(fout, ptable):
    elements_ordered = ['h', 'li', 'na', 'k', 'rb', 'cs', 'fr', 'be', 'mg', 'ca', 'sr', 'ba', 'ra', 'sc', 'y', 'ti', 'zr', 'hf', 'rf', 'v', 'nb', 'ta', 'db', 'cr', 'mo', 'w', 'sg', 'mn', 'tc', 're', 'bh', 'fe', 'ru', 'os', 'hs', 'co', 'rh', 'ir', 'mt', 'ni', 'pd', 'pt', 'ds', 'cu', 'ag', 'au', 'rg', 'zn', 'cd', 'hg', 'cn', 'ga', 'al', 'b', 'in', 'tl', 'nh', 'c', 'si', 'ge', 'sn', 'pb', 'fl', 'n', 'p', 'as', 'sb', 'bi', 'mc', 'o', 's', 'se', 'te', 'po', 'lv', 'f', 'cl', 'br', 'i', 'at', 'ts', 'ne', 'he', 'ar', 'kr', 'xe', 'rn', 'og', 'la', 'ac', 'ce', 'th', 'pr', 'pa', 'nd', 'u', 'pm', 'np', 'sm', 'pu', 'eu', 'am', 'gd', 'cm', 'tb', 'bk', 'dy', 'cf', 'ho', 'es', 'er', 'fm', 'tm', 'md', 'yb', 'no', 'lu', 'lr']
    fout.write('%%Periodic Table\n' +
                '\\setlength{\\extrarowheight}{0.95\\textheight}\n\n' +
                '\\subsection{Periodic Table of Chemical Elements}\n' +
                '\\label{anexo:periodic_table}\n\n' +
                '\\noindent\\makebox[\\textwidth]{\n' +
                '    \\begin{tabularx}{1.25\\textwidth}{c}\n' +
                '        \\scalebox{0.45}{\\begin{tikzpicture}[font=\\sffamily, transform shape]\n\n')

    for symbol in elements_ordered:
        e = ptable[symbol]
        fout.write('            \\node[name=' + e['symbol']+ ', ' + e['relative_position'] + e['category'] + '] {\\hyperlink{subsubsection::' + e['symbol'] + '}{\\NaturalElementTextFormat{' + e['number'] + '}{' + str(round(float(e['mass']),3)) + '}{' + e['symbol'] + '}{' + e['name'] + '}}};\n')
    
    fout.write('\n            \\node[name=LaLu, below of=Y, Lanthanide] {\\NaturalElementTextFormat{57-71}{}{La-Lu}{Lanthanide}};\n' +
                '            \\node[name=AcLr, below of=LaLu, Actinide] {\\NaturalElementTextFormat{89-103}{}{Ac-Lr}{Actinide}};\n' +
                '        %% Period\n            \\node[name=Period1, left of=H, PeriodLabel] {1};\n            \\node[name=Period2, left of=Li, PeriodLabel] {2};\n            \\node[name=Period3, left of=Na, PeriodLabel] {3}; \n            \\node[name=Period4, left of=K, PeriodLabel] {4}; \n            \\node[name=Period5, left of=Rb, PeriodLabel] {5};\n            \\node[name=Period6, left of=Cs, PeriodLabel] {6};\n            \\node[name=Period7, left of=Fr, PeriodLabel] {7};\n\n' +
                '        %% Group\n            \\node[name=Group1, above of=H, GroupLabel] {1 \\hfill IA};\n            \\node[name=Group2, above of=Be, GroupLabel] {2 \\hfill IIA};\n            \\node[name=Group3, above of=Sc, GroupLabel] {3 \\hfill IIIA};\n            \\node[name=Group4, above of=Ti, GroupLabel] {4 \\hfill IVB};\n            \\node[name=Group5, above of=V, GroupLabel] {5 \\hfill VB};\n            \\node[name=Group6, above of=Cr, GroupLabel] {6 \\hfill VIB};\n            \\node[name=Group7, above of=Mn, GroupLabel] {7 \\hfill VIIB};\n            \\node[name=Group8, above of=Fe, GroupLabel] {8 \\hfill VIIIB};\n            \\node[name=Group9, above of=Co, GroupLabel] {9 \\hfill VIIIB};\n            \\node[name=Group10, above of=Ni, GroupLabel] {10 \\hfill VIIIB};\n            \\node[name=Group11, above of=Cu, GroupLabel] {11 \\hfill IB};\n            \\node[name=Group12, above of=Zn, GroupLabel] {12 \\hfill IIB};\n            \\node[name=Group13, above of=B, GroupLabel] {13 \\hfill IIIA};\n            \\node[name=Group14, above of=C, GroupLabel] {14 \\hfill IVA};\n            \\node[name=Group15, above of=N, GroupLabel] {15 \\hfill VA};\n            \\node[name=Group16, above of=O, GroupLabel] {16 \\hfill VIA};\n            \\node[name=Group17, above of=F, GroupLabel] {17 \\hfill VIIA};\n            \\node[name=Group18, above of=He, GroupLabel] {18 \\hfill VIIIA};\n\n' +
                '        %% Draw dotted lines connecting Lanthanide breakout to main table\n            \\draw (LaLu.north west) edge[dotted] (La.north west)\n                        (LaLu.north east) edge[dotted] (Lu.north east)\n                        (LaLu.south west) edge[dotted] (La.south west)\n                        (LaLu.south east) edge[dotted] (Lu.south east);\n' + 
                '        %% Draw dotted lines connecting Actinide breakout to main table\n            \\draw (AcLr.north west) edge[dotted] (Ac.north west)\n                        (AcLr.north east) edge[dotted] (Lr.north east)\n                        (AcLr.south west) edge[dotted] (Ac.south west)\n                        (AcLr.south east) edge[dotted] (Lr.south east);\n\n' +
                '        %% Legend\n            \\draw[black, AlkaliMetalFill] ($(La.north -| Fr.west) + (1em,1.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkali Metal};\n            \\draw[black, AlkalineEarthMetalFill] ($(La.north -| Fr.west) + (1em,-0.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkaline Earth Metal};\n            \\draw[black, TransitionMetalFill] ($(La.north -| Fr.west) + (1em,-2.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Transition Metal};\n            \\draw[black, PostTransitionMetal] ($(La.north -| Fr.west) + (1em,-3.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Post-Transition Metal};\n            \\draw[black, MetalloidFill] ($(La.north -| Fr.west) + (1em,-5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Metalloid};\n            \\draw[black, NonmetalFill] ($(La.north -| Fr.west) + (1em,-6.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Non-metal};\n            \\draw[black, NobleGasFill] ($(La.north -| Fr.west) + (1em,-8.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Noble Gas};\n            \\draw[black, LanthanideFill] ($(La.north -| Fr.west) + (1em,-9.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Lanthanide};\n            \\draw[black, ActinideFill] ($(La.north -| Fr.west) + (1em,-11.0em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Actinide};\n            \\draw[black, UnknownFill] ($(La.north -| Fr.west) + (1em,-12.5em)$)\n                rectangle +(1em, 1em) node[right, yshift=-1ex]{Unknown};\n\n            \\node at ($(La.north -| Fr.west) + (10em,-18.0em)$) [name=elementLegend, AlkaliMetal, fill=white]\n                {\\NaturalElementTextFormat{Z}{mass}{Symbol}{Name}};\n\n'
                '        \\end{tikzpicture}}\n' +
                '    \\end{tabularx}}\n\n' +
                '\\newpage\n' + 
                '\\KOMAoptions{paper=portrait,pagesize}\n' +
                '\\recalctypearea\n' +
                '\\newgeometry{margin = 4cm}\n\n')


# Imprimir gráfico com número de ocorrências de cada elemento químico
def printElemsOccurrencesApp(fout, ptable):
    elems = list(filter(lambda e: e['occurrences']!=0, ptable.values()))

    if len(elems) > 0:
        elems.sort(key=lambda e: e['occurrences'])
        m =  roundup(max(map(lambda e: e['occurrences'], elems)))
        i = 2
        colors = {
                    'AlkaliMetal': 'blue!55',
                    'AlkalineEarthMetal': 'blue!40',
                    'TransitionMetal': 'blue!25',
                    'PostTransitionMetal': 'orange!25',
                    'Metalloid': 'yellow!15',
                    'Nonmetal': 'green!25',
                    'Halogen': 'green!40',
                    'NobleGas': 'green!55',
                    'Lanthanide': 'purple!50',
                    'Actinide': 'purple!25',
                    'Unknown': 'gray!25'
                } 

        fout.write('%% Chemical Elements Occurrences\n' +
                    '\\subsection{Chemical Elements Occurrences}\n' +
                    '\\label{anexo:elements_occurrences}\n\n' +
                    '\\scalebox{0.90}{\n')

        for elem in elems:
            if i % 34 == 0:
                fout.write('  \\end{bchart}\n\n')
            if i == 2 or i % 34 == 0:
                fout.write('  \\begin{bchart}[max=' + str(m) + ']\n')
            fout.write('    \\bcbar[label=' + elem['symbol'] + ', color=' + colors[elem['category']] + ']{' + str(elem['occurrences']) + '}\n' +
                       '    \\bcskip{3pt}\n')
            i += 1
        
        if i > 2: 
            fout.write('  \\end{bchart}\n' +
                       '}\n\n' +
                       '\\smallskip\n\n' +
                       '%%Legend\n\\begin{figure}[!h]\n  \\centering\n  \\scalebox{0.80}{\n    \\begin{tikzpicture}\n      \\draw[black, AlkaliMetalFill] ($(La.north -| Fr.west) + (1em,1.0em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkali Metal};\n      \\draw[black, AlkalineEarthMetalFill] ($(La.north -| Fr.west) + (1em,-0.5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Alkaline Earth Metal};\n      \\draw[black, TransitionMetalFill] ($(La.north -| Fr.west) + (1em,-2.0em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Transition Metal};\n      \\draw[black, PostTransitionMetal] ($(La.north -| Fr.west) + (1em,-3.5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Post-Transition Metal};\n      \\draw[black, MetalloidFill] ($(La.north -| Fr.west) + (1em,-5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Metalloid};\n      \\draw[black, NonmetalFill] ($(La.north -| Fr.west) + (1em,-6.5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Non-metal};\n      \\draw[black, NobleGasFill] ($(La.north -| Fr.west) + (1em,-8.0em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Noble Gas};\n      \\draw[black, LanthanideFill] ($(La.north -| Fr.west) + (1em,-9.5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Lanthanide};\n      \\draw[black, ActinideFill] ($(La.north -| Fr.west) + (1em,-11.0em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Actinide};\n      \\draw[black, UnknownFill] ($(La.north -| Fr.west) + (1em,-12.5em)$)\n          rectangle +(1em, 1em) node[right, yshift=-1ex]{Unknown};\n    \\end{tikzpicture}\n  }\n\\end{figure}\n\n'
                       '\\newpage\n\n')
    

# Imprimir gráfico com número de ocorrências de cada fórmula química
def printFormulasOccurrencesApp(fout, formulas_found):
    formulas = list(formulas_found.items())

    if len(formulas) > 0:
        formulas.sort(key=lambda e: e[1])
        m =  roundup(max(map(lambda e: e[1], formulas)))
        i = 2

        fout.write('%% Chemical Formulas Occurrences\n' +
                    '\\subsection{Chemical Formulas Occurrences}\n' +
                    '\\label{anexo:formulas_occurrences}\n\n')

        for f in formulas:
            if i % 34 == 0:
                fout.write('\\end{bchart}\n\n')
            if i == 2 or i % 34 == 0:
                fout.write('\\begin{bchart}[max=' + str(m) + ']\n')
            fout.write('    \\bcbar[label=' + f[0] + ']{' + str(f[1]) + '}\n' +
                       '    \\bcskip{3pt}\n')
            i += 1
        
        if i > 2: 
            fout.write('\\end{bchart}\n\n\\newpage\n\n')
    

# Imprimir informação dos elementos químicos nos apêndices
def printElemsInfoApp(fout, resourcespath, ptable):
    fout.write('%% Chemical Elements Information\n' +
                '\\subsection{Chemical Elements Information}\n' +
                '\\label{anexo:elements_info}\n\n')

    for (k,v) in ptable.items():
        fout.write('\\hypertarget{subsubsection::' + v['symbol'] + '}{}\\subsubsection{' + v['name'] + ' (' + v['symbol'] + ')}\n\n')
        if 'number' in v.keys() and v['number'] and v['number'] != 'null':
            fout.write('\\textit{Number}: ' + v['number'] + '\n\n')
        if 'category' in v and v['category'] and v['category'] != 'null': 
            fout.write('\\textit{Category}: ' + v['category'] + '\n\n')
        if 'phase' in v and v['phase'] and v['phase'] != 'null': 
            fout.write('\\textit{Phase at STP}: ' + v['phase'] + '\n\n')
        if 'appearance' in v and v['appearance'] and v['appearance'] != 'null': 
            fout.write('\\textit{Appearance}: ' + v['appearance'] + '\n\n')
        if 'color' in v and v['color'] and v['color'] != 'null': 
            fout.write('\\textit{Color}: ' + v['color'] + '\n\n')
        if 'atomic_mass' in v and v['atomic_mass'] and v['atomic_mass'] != 'null':
            fout.write('\\textit{Atomic Mass}: ' + v['atomic_mass'] + '\n\n')
        if 'melt' in v and v['melt'] and v['melt'] != 'null':
            fout.write('\\textit{Melting Point}: ' + v['melt'] + ' K\n\n')
        if 'boil' in v and v['boil'] and v['boil'] != 'null':
            fout.write('\\textit{Boiling Point}: ' + v['boil'] + ' K\n\n')
        if 'molar_heat' in v and v['molar_heat'] and v['molar_heat'] != 'null':
            fout.write('\\textit{Molar Heat}: ' + v['molar_heat'] + ' J/(mol·K)\n\n')
        if 'density' in v and v['density'] and v['density'] != 'null':
            fout.write('\\textit{Density}: ' + v['density'] + ' g/L\n\n')
        if 'summary' in v and v['summary'] and v['summary'] != 'null':
            fout.write('\\textit{Description}: ' + v['summary'] + '\n\n')
        if 'discovered_by' in v and v['discovered_by'] and v['discovered_by'] != 'null':
            fout.write('\\textit{Discovered By}: ' + v['discovered_by'] + '\n\n')
        if 'named_by' in v and v['named_by'] and v['named_by'] != 'null':
            fout.write('\\textit{Named By}: ' + v['named_by'] + '\n\n')
        if 'spectral_img' in v and v['spectral_img'] and v['spectral_img'] != 'null':
            fout.write('\\immediate\\write18{sudo wget -nc -nd -q -r -P ' + resourcespath + '/spectral_img -A jpeg,jpg,bmp,gif,png ' + v['spectral_img'] + '}\n' +
                '\\begin{figure}[!ht]\n    \\centering\n    \\includegraphics[width=12cm]{' + resourcespath + '/spectral_img/' + v['spectral_img'].split('/')[-1] + '}\n    \\caption{' + v['name'] + ' Spectral Image}\n\\end{figure}\n\n')


# Imprimir fim do documento latex (com apêndices)
def printEndDocument(fout, resourcespath, ptable, formulas_found):
    # Apendices
    fout.write('\n\\setcounter{section}{0}\n' +
                '\\setcounter{subsection}{0}\n\n' +
                # Página horizontal para a TP
                '\\newpage\n' +
                '\\KOMAoptions{paper=landscape,pagesize}\n' +
                '\\recalctypearea\n' +
                '\\thispagestyle{empty}\n\n' +
                # Apêndices
                '%% Appendices\n' +
                '\\appendixpage\n' +
                '\\renewcommand{\\thesubsection}{\\Alph{subsection}}\n\n')
    printPeriodicTableApp(fout, ptable)
    printElemsOccurrencesApp(fout, ptable)
    printFormulasOccurrencesApp(fout, formulas_found)
    printElemsInfoApp(fout, resourcespath, ptable)
    
    fout.write('\\end{document}\n')