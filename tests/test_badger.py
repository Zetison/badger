from collections import OrderedDict

from badger import badger, input

class TestCall:
    def test_notemp(self):
        setup = input.empty_setup(
            ['echo'],
            cmdargs=['a=$alpha$', 'b=$bravo$', 'c=$charlie$'],
            parameters=OrderedDict([('alpha', [2, 4]), ('bravo', ['a', 'b'])]),
            dependencies=OrderedDict([('charlie', 'alpha**2')]),
            parse=['(?P<out>.+)']
            )
        stuff = badger.work(input.parse_args(['foo']), setup)
        assert stuff['results']['out'] == [
            'a=2 b=a c=4',
            'a=2 b=b c=4',
            'a=4 b=a c=16',
            'a=4 b=b c=16',
            ]

    def test_temp(self):
        setup = input.empty_setup(
            ['cat'],
            cmdargs=['tests/template.temp'],
            templates=['tests/template.temp'],
            parameters=OrderedDict([('alpha', ['a', 'b', 'c']), ('bravo', [1, 2, 3])]),
            parse=['(?P<out>.+)']
            )
        stuff = badger.work(input.parse_args(['foo']), setup)
        assert stuff['results']['out'] == [
            'a=a b=1', 'a=a b=2', 'a=a b=3',
            'a=b b=1', 'a=b b=2', 'a=b b=3',
            'a=c b=1', 'a=c b=2', 'a=c b=3',
            ]


