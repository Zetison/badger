from collections import OrderedDict

from badger import badger, input

class TestCall:
    def test(self):
        setup = input.empty_setup(
            ['echo'],
            cmdargs=['a=$alpha', 'b=$bravo', 'c=$charlie'],
            parameters=OrderedDict([('alpha', [2, 4]), ('bravo', ['a', 'b'])]),
            dependencies=OrderedDict([('charlie', 'alpha**2')]),
            parse=['^(?P<out>.*)$'],
        )
        stuff = badger.work(input.parse_args(['foo']), setup)
        assert stuff['results']['out'] == [
            'a=2 b=a c=4',
            'a=2 b=b c=4',
            'a=4 b=a c=16',
            'a=4 b=b c=16',
        ]
