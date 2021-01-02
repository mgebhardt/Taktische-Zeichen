#! /usr/bin/env python3

""" j2build """

__author__ = "Mathias Gebhardt"
__email__ = "mathias@mathiasgebhardt.de"
__version__ = "1.0.0"


import io, os, sys
import argparse

import yaml

import jinja2

def render(j2_template, data, output_file):
    output = j2_template.render(data)
    with io.open(output_file, 'wt', encoding='utf-8') as f:
        f.write(output)
        f.close()

parser = argparse.ArgumentParser(
        prog='j2build',
        description='Build tool for Jinja2 templates with yaml data files.',
        epilog=''
    )
parser.add_argument('-v', '--version', action='version',
                    version='j2build {0}, Jinja2 {1}'.format(__version__, jinja2.__version__))

parser.add_argument('templates', help='Template folder path')
parser.add_argument('input_file', help='yaml input data file')
parser.add_argument('output', help="Output data file or path")
args = parser.parse_args(sys.argv[1:])

# Load and parse input data
data_string = open(args.input_file).read()
data = yaml.load(data_string, yaml.FullLoader)

# Init Jinja2 environment
# Use current working directory as template search path
j2_env = jinja2.Environment(\
    trim_blocks=True, \
    lstrip_blocks=True, \
    keep_trailing_newline=True, \
    undefined=jinja2.StrictUndefined, \
    loader=jinja2.FileSystemLoader(os.getcwd()))

# Get template name by top level name
# TODO: iterate through all top level entities to support different types within one yaml file
template = list(data)[0]

# Load the selected template
j2_template = j2_env.get_template(os.path.join(args.templates, template + ".j2"))

# Now its time to render the data
# The template requires a dict with <<Template>> as the top level entity

if(type(data[template]) is not list):
    # Only a single entry --> just render the data and be happy ;)
    # TODO: this might fail if different types are present
    if not data[template].get('Legacy'):
        render(j2_template,data,args.output)
else:
    # we got a list --> we have to build multiple data sets
    for data_set in data[template]:
        tmp_data = {template : data_set}
        if data_set.get('FileName'):
            file_name = data_set.get('FileName')
        else:
            if data_set.get('Typ'):
                file_name = '_'.join([data_set.get('Name'), data_set.get('Typ')])
            else:
                file_name = data_set.get('Name')
        if not data_set.get('Legacy'):
            render(j2_template,tmp_data,os.path.join(os.path.dirname(args.output), file_name + '.svg'))
