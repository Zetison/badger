#!/usr/bin/env python3

# Copyright (C) 2015 SINTEF ICT,
# Applied Mathematics, Norway.
#
# Contact information:
# E-mail: eivind.fonn@sintef.no
# SINTEF ICT, Department of Applied Mathematics,
# P.O. Box 4760 Sluppen,
# 7045 Trondheim, Norway.
#
# This file is part of BADGER.
#
# BADGER is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# BADGER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with GoTools. If not, see
# <http://www.gnu.org/licenses/>.
#
# In accordance with Section 7(b) of the GNU Affero General Public
# License, a covered work must retain the producer line in every data
# file that is created or manipulated using GoTools.
#
# Other Usage
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as you
# develop commercial activities involving BADGER without disclosing the
# source code of your own applications.
#
# This file may be used in accordance with the terms contained in a
# written agreement between you and SINTEF ICT.

import yaml
import sys
import tempfile
import shutil
import subprocess
import re
import argparse

from socket import gethostname
from datetime import datetime
from itertools import product
from collections import OrderedDict
from os.path import join

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def coerce_list(dictionary, key, split=None):
    if not key in dictionary:
        dictionary[key] = []
    if isinstance(dictionary[key], str):
        if split:
            dictionary[key] = dictionary[key].split(split)
        else:
            dictionary[key] = [dictionary[key]]

def interpolate_vars(string, namespace):
    for name, value in namespace.items():
        string = string.replace('$' + name, str(value))
    return string

def coerce_types(dictionary, types):
    type_map = {'float': float,
                'str': str,
                'int': int,
                'bool': bool}
    for key, val in dictionary.items():
        if key in types:
            dictionary[key] = type_map[types[key]](val)

def output_yaml(data, types, fn):
    with open(fn, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def output_py(data, types, fn):
    code = """from numpy import array, zeros

metadata = {'hostname': '%(hostname)s',
            'time': '%(time)s'}
""" % {'hostname': data['metadata']['hostname'],
       'time': data['metadata']['time']}

    def fmt(v):
        if isinstance(v, str):
            return "'%s'" % v
        return str(v)

    size = []
    for p in data['parameters']:
        code += '{} = array([{}])\n'.format(p['name'], ', '.join(fmt(d) for d in p['values']))
        size.append(len(p['values']))
    size = '({})'.format(', '.join(str(s) for s in size))

    for k, vals in data['results'].items():
        code += '{} = zeros({}, dtype={})\n'.format(k, size, types[k])
        code += '{}.flat[:] = [{}]\n'.format(k, ', '.join(fmt(v) for v in vals))

    with open(fn, 'w') as f:
        f.write(code)


if __name__ == '__main__':
    FORMATS = {
        'yaml': output_yaml,
        'py': output_py,
    }

    parser = argparse.ArgumentParser(description='Batch job runner.')
    parser.add_argument('-o', '--output', required=False, default='output.yaml',
                        help='The output file')
    parser.add_argument('-f', '--format', required=False, default=None,
                        choices=FORMATS, help='The output format')
    parser.add_argument('file', help='Configuration file for the batch job')
    args = parser.parse_args()

    if args.format is None:
        try:
            args.format = args.output.split('.')[-1]
            assert args.format in FORMATS
        except (AssertionError, IndexError):
            print('Unable to determine output format from filename "{}"'.format(args.output))
            sys.exit(1)

    with open(args.file, 'r') as f:
        setup = ordered_load(f, yaml.SafeLoader)

    coerce_list(setup, 'templates')
    coerce_list(setup, 'files')
    coerce_list(setup, 'cmdargs', split=' ')
    coerce_list(setup, 'parse')
    for key in ['dependencies', 'types']:
        if key not in setup:
            setup[key] = {}

    basic_cmdargs = [setup['executable']] + setup['cmdargs']

    regexps = [re.compile(r) for r in setup['parse']]
    results = []

    for tp in product(*(l for _, l in setup['parameters'].items())):
        namespace = dict(zip(setup['parameters'], tp))
        for name, expr in setup['dependencies'].items():
            namespace[name] = eval(str(expr), {}, namespace)

        templates = {}
        for fn in setup['templates']:
            with open(fn, 'r') as f:
                data = f.read()
            templates[fn] = interpolate_vars(data, namespace)

        with tempfile.TemporaryDirectory() as path:
            for fn, data in templates.items():
                with open(join(path, fn), 'w') as f:
                    f.write(data)
            for fn in setup['files']:
                shutil.copy(fn, join(path, fn))

            print('Running ' + ', '.join('{}={}'.format(var, namespace[var])
                                         for var in setup['parameters']) + ' ...')
            cmdargs = [interpolate_vars(arg, namespace) for arg in basic_cmdargs]
            output = subprocess.check_output(cmdargs, cwd=path).decode()

            result = {}
            for r in regexps:
                m = None
                for m in r.finditer(output): pass
                if m:
                    result.update(m.groupdict())
            coerce_types(result, setup['types'])
            results.append(result)

            print('  ' + ', '.join('{}={}'.format(*t) for t in result.items()))

    all_output = set().union(*results)
    for out in all_output:
        if out not in setup['types']:
            setup['types']['out'] = 'str'

    final = {
        'metadata': {
            'hostname': gethostname(),
            'time': str(datetime.now()),
        },
        'parameters': [{'name': param, 'values': values}
                       for param, values in setup['parameters'].items()],
        'results': {output: [result.get(output) for result in results]
                    for output in all_output},
    }

    FORMATS[args.format](final, setup['types'], args.output)
