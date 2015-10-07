import argparse
import shlex
import sys
import yaml

from collections import OrderedDict

import badger.output as output


def coerce_list(dictionary, key, split=None, required=False):
    if not required:
        if key not in dictionary:
            dictionary[key] = []
    if isinstance(dictionary[key], str):
        if isinstance(split, str):
            dictionary[key] = dictionary[key].split(split)
        elif split:
            dictionary[key] = split(dictionary[key])
        else:
            dictionary[key] = [dictionary[key]]


def parse_args(input=None):
    parser = argparse.ArgumentParser(description='Batch job runner.')
    parser.add_argument('-o', '--output', required=False, default='output.yaml',
                        help='The output file')
    parser.add_argument('-f', '--format', required=False, default=None,
                        choices=output.FORMATS, help='The output format')
    parser.add_argument('file', help='Configuration file for the batch job')
    args = parser.parse_args(input)

    if args.format is None:
        try:
            args.format = args.output.split('.')[-1]
            assert args.format in output.FORMATS
        except (AssertionError, IndexError):
            print('Unable to determine output format from filename "{}"'.format(args.output))
            sys.exit(1)

    return args


# YAML is unordered by default, this is an ordered loader
# Thanks http://stackoverflow.com/a/21912744/2729168
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


def load_setup(fn):
    with open(fn, 'r') as f:
        setup = ordered_load(f, yaml.SafeLoader)
    setup = setup or {}

    coerce_list(setup, 'templates')
    coerce_list(setup, 'files')
    coerce_list(setup, 'cmdargs', split=shlex.split)
    coerce_list(setup, 'executable', split=shlex.split, required=True)
    coerce_list(setup, 'parse')
    for key in ['dependencies', 'types', 'parameters']:
        if key not in setup:
            setup[key] = {}

    for key in setup['dependencies']:
        setup['dependencies'][key] = str(setup['dependencies'][key])

    return setup


def empty_setup(executable='', **kwargs):
    ret = {
        'templates': [],
        'files': [],
        'executable': executable,
        'cmdargs': [],
        'parameters': OrderedDict(),
        'dependencies': OrderedDict(),
        'parse': [],
        'types': OrderedDict(),
        }

    ret.update(kwargs)
    return ret
