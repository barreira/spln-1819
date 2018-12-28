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
