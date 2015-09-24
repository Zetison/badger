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

if __name__ == '__main__':
    setup_file = sys.argv[1]

    with open(setup_file, 'r') as f:
        setup = ordered_load(f, yaml.SafeLoader)

    coerce_list(setup, 'templates')
    coerce_list(setup, 'files')
    coerce_list(setup, 'params', split=' ')
    if 'dependencies' not in setup:
        setup['dependencies'] = {}

    basic_args = [setup['executable']] + setup['params']

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
            args = [interpolate_vars(arg, namespace) for arg in basic_args]
            print(args)
            output = subprocess.check_output(args, cwd=path).decode()

            result = {}
            for r in regexps:
                m = None
                for m in r.finditer(output): pass
                if m:
                    result.update(m.groupdict())
            results.append(result)

            print('  ' + ', '.join('{}={}'.format(*t) for t in result.items()))

    all_output = set().union(*results)

    # TODO: implement alternative output formats

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

    with open('output.yaml', 'w') as f:
        yaml.dump(final, f, default_flow_style=False)
