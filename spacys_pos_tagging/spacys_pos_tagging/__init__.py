#!/usr/bin/python3

from .app import process_args
from .pos_tagging import add_tokenizer_exceptions, generate_dependencies_graph, \
generate_information, generate_pos_chart, generate_tagged_text
