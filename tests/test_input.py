from nose.tools import raises, assert_raises
from collections import OrderedDict
from operator import methodcaller

from badger import input


class TestArgs:
    def test_file(self):
        args = input.parse_args(['blergh'])
        assert args.file == 'blergh'
        assert args.output == 'output.yaml'
        assert args.format == 'yaml'

    def test_output(self):
        args = input.parse_args(['-o', 'test.py', 'argh'])
        assert args.file == 'argh'
        assert args.output == 'test.py'
        assert args.format == 'py'

    def test_format(self):
        args = input.parse_args(['-f', 'py', 'yoink'])
        assert args.file == 'yoink'
        assert args.output == 'output.yaml'
        assert args.format == 'py'

    def test_all(self):
        args = input.parse_args(['-o', 'foo', '-f', 'yaml', 'bar'])
        assert args.file == 'bar'
        assert args.output == 'foo'
        assert args.format == 'yaml'

    def test_incorrect_format(self):
        with assert_raises(SystemExit):
            input.parse_args(['-o', 'foo', '-f', 'baz', 'bar'])
        with assert_raises(SystemExit):
            input.parse_args(['-o', 'foo.baz', 'bar'])

    @raises(SystemExit)
    def test_no_file(self):
        input.parse_args([])


class TestSetup:
    @raises(KeyError)
    def test_empty(self):
        input.load_setup('test_input_empty.yaml')

    def test_minimal(self):
        setup = input.load_setup('test_input_minimal.yaml')
        for k in ['executable']:
            setup[k] = list(map(methodcaller('render'), setup[k]))

        assert setup['executable'] == ['alpha', 'bravo', 'charlie']
        for k in ['templates', 'files', 'cmdargs', 'parse']:
            assert setup[k] == []
        for k in ['dependencies', 'types']:
            assert setup[k] == {}

    def test_basic(self):
        setup = input.load_setup('test_input_basic.yaml')
        for k in ['templates', 'files', 'executable', 'cmdargs']:
            setup[k] = list(map(methodcaller('render'), setup[k]))

        assert setup['templates'] == ['alpha bravo']
        assert setup['files'] == ['one', 'two', 'three']
        assert setup['executable'] == [r'charlie \n delta', 'echo']
        assert setup['cmdargs'] == ['echo', 'foxtrot', 'golf', r'hotel \ india']

        assert setup['parameters'] == OrderedDict([
            ('degree', [1, 2]),
            ('elements', [8, 16]),
            ('timestep', [0.1, 0.05]),
        ])
        assert all(isinstance(v, int) for v in setup['parameters']['degree'])
        assert all(isinstance(v, int) for v in setup['parameters']['elements'])
        assert all(isinstance(v, float) for v in setup['parameters']['timestep'])

        assert setup['dependencies'] == OrderedDict([
            ('raiseorder', 'degree - 1'),
            ('refineu', 'elements//8 - 1'),
            ('refinev', 'elements - 1'),
            ('endtime', '10'),
        ])

        assert setup['parse'] == ['regexp1', r'complicated regexp \s+']

        assert setup['types'] == OrderedDict([
            ('p_rel_l2', 'float'),
            ('cpu_time', 'bool'),
            ('wall_time', 'str'),
        ])
