# coding=utf-8
#!/usr/bin/python3

"""
Web app and terminal client to use spaCy's features
"""

from spacys_pos_tagging import execute
import sys
import getopt

INFO_OUT = ''
POS_CHART_OUT = ''
TAGGED_TEXT_OUT = ''
GRAPHS_OUT = ''
LANG = 'pt'
INPUTFILE = ''

ERROR = 'USAGE:\tpython3 app.py [(-i <outputfile> | -p <outputfile> | -t <outputfile> | ' + \
        '-g <outputfile>) [-l <LANGuage>] <INPUTFILE>]\n\n' + \
        'OPTIONS:\n' + \
        '\t-l\tLANGuage - \'pt\' (default) or \'en\'\n' + \
        '\t-i\treturns table with information about tokens to outputfile (or \'shell\')\n' + \
        '\t-p\tgenerates bar chart with POS tag frequence to outputfile\n' + \
        '\t-t\treturns tagged text to outputfile (or \'shell\')\n' + \
        '\t-g\tgenerates dependencies graphs to outputfile.svg\n' +\
        '* if no options are provided, a web server will be initialized, where the input will ' + \
        'be inserted and the output presented.'

# Processar opções/argumentos do comando utilizado
try:
    OPTS, ARGS = getopt.getopt(sys.argv[1:], "i:p:t:g:l:hv", ["info=", "pos-chart=", "tagged-text=",
                                                              "graphs=", "LANG=", "help", "version"]
                              )
except getopt.GetoptError:
    print(ERROR)
    sys.exit(2)
for opt, arg in OPTS:
    if opt in ('-h', '--help'):
        print(ERROR)
        sys.exit()
    elif opt in ('-v', '--version'):
        print('Version 1.0')
        sys.exit()
    elif opt in ("-i", "--info"):
        INFO_OUT = arg
    elif opt in ("-p", "--pos-chart"):
        POS_CHART_OUT = arg
    elif opt in ("-t", "--tagged-text"):
        TAGGED_TEXT_OUT = arg
    elif opt in ("-g", "--graphs"):
        GRAPHS_OUT = arg
    elif opt in ("-l", "--LANG"):
        LANG = arg

if INFO_OUT or POS_CHART_OUT or TAGGED_TEXT_OUT or GRAPHS_OUT:
    if len(ARGS) == 1:
        INPUTFILE = ARGS[0]
    else:
        print(ERROR)
        sys.exit(2)
elif ARGS:
    print(ERROR)
    sys.exit(2)

execute(INFO_OUT, POS_CHART_OUT, TAGGED_TEXT_OUT, GRAPHS_OUT, LANG, INPUTFILE)
