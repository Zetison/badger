#!/usr/bin/env python3

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

if __name__ == '__main__':
    setup_file = sys.argv[1]

    with open(setup_file, 'r') as f:
        setup = ordered_load(f, yaml.SafeLoader)

    args = [setup['executable']]
    if isinstance(setup['params'], list):
        args.extend(setup['params'])
    elif isinstance(setup['params'], str):
        args.extend(setup['params'].split(' '))
    args.append(setup['template'])

    regexps = [re.compile(r) for r in setup['parse']]
    results = []

    for tp in product(*(l for _, l in setup['parameters'].items())):
        namespace = dict(zip(setup['parameters'], tp))
        for name, expr in setup['dependencies'].items():
            namespace[name] = eval(str(expr), {}, namespace)

        with open(setup['template'], 'r') as f:
            xinp = f.read()
        for name, value in namespace.items():
            xinp = xinp.replace('$' + name, str(value))

        with tempfile.TemporaryDirectory() as path:
            with open(join(path, setup['template']), 'w') as f:
                f.write(xinp)
            for fn in setup['files']:
                shutil.copy(fn, join(path, fn))

            print('Running ' + ', '.join('{}={}'.format(var, namespace[var])
                                         for var in setup['parameters']) + ' ...')

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
