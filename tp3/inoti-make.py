# coding=utf-8

""" inoti-make

An implementation of the inotify library that used a configuration file to watch directories and
perform actions based on events.

Expects a configuration file as follows:

FoldersPath:    ['FOLDER1_PATH', 'FOLDER2_PATH', ...]
NamesRegex:     ['FILENAME_1', 'FOLDER_2', ...]
EV1|EV2|...:    [('SHELL_COMMAND', 'command'), ...]
EV3|...:        [('SHELL_COMMAND', 'command'), ...]
NamesRegex:     ['FILENAME_1', 'FOLDER_2', ...]
EV1|EV2|...:    [('SHELL_COMMAND', 'command'), ...]
EV3|...:        [('SHELL_COMMAND', 'command'), ...]

FoldersPath:    ['FOLDER3_PATH', 'FOLDER4_PATH', ...]
...
"""

import os
import re
import sys
import ast
import inotify.adapters


def parse(config_path):
    """
    Parses the configuration file
    """
    config = {}
    folders_path = []
    names_regex = []

    with open(config_path, 'r') as fd:
        for line in fd:
            if re.match('FoldersPath:', line, flags=re.RegexFlag.IGNORECASE):
                folders_path = [s.strip() for s in
                                ast.literal_eval(line[line.index(':')+1:].strip())]
                names_regex = []
                # TODO: Verificar que folders_path seja uma lista e que todas as diretorias existam
                for path in folders_path:
                    if not path in config:
                        config[path] = {}
                        config[path][0] = False
            elif re.match('NamesRegex:', line, flags=re.RegexFlag.IGNORECASE):
                names_regex = [s.strip() for s in
                               ast.literal_eval(line[line.index(':')+1:].strip())]
                # TODO: Verificar que names_regex seja uma lista
                for path in folders_path:
                    for name in names_regex:
                        if name not in config[path]:
                            config[path][name] = {}
            elif re.match('Recursive:', line, flags=re.RegexFlag.IGNORECASE):
                config[path][0] = line[line.index(':')+1:].strip().lower() == 'true'
            elif not re.search(r'^\s*$', line):
                ops = [s.strip() for s in line[:line.index(':')].split('|')]
                actions = ast.literal_eval(line[line.index(':')+1:].strip())
                # TODO: Verificar que opções sejam válidas
                # TODO: Verificar que ações sejam válidas (tuplos, tipos de ação, ...)
                for path in folders_path:
                    for name in names_regex:
                        for op in ops:
                            if op not in config[path][name]:
                                config[path][name][op] = set(actions)
                            else:
                                config[path][name][op].update(actions)
            else:
                folders_path = []
                names_regex = []
    return config


def intersection(lst1, lst2):
    """
    Returns the intersection of two lists of elements
    """
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def exec_actions(actions, watch_path, var_name_ext):
    """
    Executes the actions defined in the configuration file in the watched directory
    """
    var_name = var_name_ext.rsplit('.', 1)[0]
    current_dir = os.getcwd()
    os.chdir(watch_path)
    watch_path_absolute = os.getcwd()
    for action_type, action in actions:
        action_name = action.replace('$NAME_EXT', var_name_ext)\
                            .replace('$NAME', var_name)\
                            .replace('$CURRENT_DIR', current_dir)\
                            .replace('$WATCH_DIR_LAST', watch_path_absolute.split('/')[-1])\
                            .replace('$WATCH_DIR', watch_path_absolute)
        if action_type == 'SHELL_COMMAND':
            os.system(action_name)
    os.chdir(current_dir)


def concat_config(config, new_config):
    """
    Adds new configurations to the existing configuration variable.
    """
    for new_path in new_config:
        if new_path not in config:
            config[new_path] = new_config[new_path]
        else:
            config[new_path][0] = config[new_path][0] or new_config[new_path][0]
            for filename in config[new_path]:
                if filename != 0:
                    if filename in new_config[new_path]:
                        for op in config[new_path][filename]:
                            if op in new_config[new_path][filename]:
                                new_config[new_path][filename][op]\
                                    .update(config[new_path][filename][op])
                            else:
                                new_config[new_path][filename][op] = config[new_path][filename][op]
                    else:
                        new_config[new_path][filename] = config[new_path][filename]
    return config


def listen_folders(config):
    """
    Adds watchers to the watched folders, listens for events and executes actions.
    """
    i = inotify.adapters.Inotify()

    new_config = {}
    for watch_path in config:
        i.add_watch(watch_path)
        # Se é recursivo, adiciona watch a cada subdiretoria
        if config[watch_path][0]:
            subdirs = [x[0] for x in os.walk(watch_path)]
            for dir_path in subdirs:
                if dir_path not in config and dir_path not in new_config:
                    i.add_watch(dir_path)
                entry = {dir_path: config[watch_path]}
                new_config = concat_config(new_config, entry)
    config = concat_config(config, new_config)

    try:
        for event in i.event_gen(yield_nones=False):
            (_, type_names, watch_path, filename) = event
            if 'IN_CREATE' in type_names and os.path.isdir(watch_path + '/' + filename) \
                    and config[watch_path][0]:
                dir_path = watch_path + '/' + filename
                if dir_path not in config:
                    i.add_watch(dir_path)
                entry = {dir_path: config[watch_path]}
                config = concat_config(config, entry)
            # Obter todos os nomes de ficheiros sobre os quais atuar
            filename_matches = []
            for name_regex in config[watch_path].keys():
                if name_regex != 0 and re.search(name_regex, filename):
                    filename_matches.append(name_regex)
            # Executar ações
            for name_regex in filename_matches:
                types = intersection(type_names, config[watch_path][name_regex].keys())
                for type_name in types:
                    exec_actions(config[watch_path][name_regex][type_name], watch_path, filename)

    except KeyboardInterrupt:
        for watch_path in config:
            i.remove_watch(watch_path)
        print('FINISHED')


def main():
    """
    Main function that expects a configuration file. Calls the parsing function on this file and
    uses the result to add watchers to the watched folders, listen for events and execute actions
    """
    if len(sys.argv) != 2:
        print('USAGE:\tpython3 inoti-make.py <CONFIG_FILE>')
        exit(1)
    config = parse(sys.argv[1])
    listen_folders(config)


if __name__ == '__main__':
    main()
