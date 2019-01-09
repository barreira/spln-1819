# inoti-make

## Ficheiro de configuração

´´´
FoldersPath:    ['FOLDER1_PATH', 'FOLDER2_PATH', ...]
NamesRegex:     ['FILENAME_1', 'FOLDER_2', ...]
OP1|OP2|...:    [('OS', 'OS Command'), ('P', 'PYTHON Command'), ...]
OP3|...:        [('OS', 'OS Command'), ('P', 'PYTHON Command'), ...]
NamesRegex:     ['FILENAME_1', 'FOLDER_2', ...]
OP1|OP2|...:    [('OS', 'OS Command'), ('P', 'PYTHON Command'), ...]
OP3|...:        [('OS_C', 'OS Command'), ('P_S', 'PYTHON_path_script'), ...]

FoldersPath:    ['FOLDER3_PATH', 'FOLDER4_PATH', ...]
...
´´´

**Operações permitidas**:

+ IN_ACCESS
+ IN_MODIFY
+ IN_ATTRIB
+ IN_CLOSE_WRITE
+ IN_CLOSE_NOWRITE
+ IN_OPEN
+ IN_MOVED_FROM
+ IN_MOVED_TO
+ IN_CREATE
+ IN_DELETE
+ IN_DELETE_SELF
+ IN_MOVE_SELF
+ IN_ALL_EVENTS

**TAGs permitidas nos comandos**:

+ $NAME
+ $NAME_EXT

## Ideias

Problemas:

+ Remover e mudar nomes de diretorias vigiadas não atualiza watches. [MAFALDA]

Código/Demonstração:

+ Adicionar ao gitignore alguns ficheiros automaticamente [JOÃO]

+ Conversor de imagem de texto digitalizado para texto [JOÃO]
    https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
    https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/

+ Spell checker e corrector de português (atenção a tracino - jantasse/janta-se) [MAFALDA]
    https://github.com/mammothb/symspellpy (spell corrector)
    http://norvig.com/spell-correct.html (spell corrector - re)
    https://github.com/blatinier/pyhunspell (spell checker)
    https://github.com/WojciechMula/aspell-python (spell checker)

    https://rustyonrampage.github.io/text-mining/2017/11/28/spelling-correction-with-python-and-nltk.html
    https://github.com/tokestermw/spacy_hunspell
    https://github.com/pirate/spellchecker

    # ASPELL
    sudo apt-get install libaspell-dev
    python3 -m pip install pip==18.0
    sudo pip3 install aspell-python-py3
    Dicionário pt - https://ftp.gnu.org/gnu/aspell/dict/0index.html
                    ./configure
                    make
                    make install
                    python: s = aspell.Speller('lang', 'pt_PT')

    #HUNSPELL
    sudo apt-get install libhunspell-dev
    sudo pip3 install hunspell
    Dicionário pt - http://natura.di.uminho.pt/download/sources/Dictionaries/hunspell/LATEST/

    #symspellpy
    sudo pip3 install symspellpy
    Dicionário pt - https://invokeit.wordpress.com/frequency-word-lists/

    # SpaCy - https://medium.com/@akankshamalhotra24/introduction-to-libraries-of-nlp-in-python-nltk-vs-spacy-42d7b2f128f2

Relatório:

+ Calcular métricas de performance

Dicas:

+ Processar enormes quantidades de texto
+ Processar Português
+ Ir buscar dados diretamente à internet