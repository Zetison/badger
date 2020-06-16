from pathlib import Path

import numpy as np

from badger import Case


DATADIR = Path(__file__).parent / 'data'

def test_parse():
    case = Case(DATADIR / 'valid' / 'diverse.yaml')

    for name, param in case._parameters.items():
        assert param.name == name
    assert case._parameters['alpha'].values == [1, 2]
    assert case._parameters['bravo'].values == [1.0, 2.0]
    assert case._parameters['charlie'].values == [3, 4.5]
    np.testing.assert_allclose(case._parameters['delta'].values, [0.0, 0.25, 0.5, 0.75, 1.0], atol=1e-6, rtol=1e-6)
    np.testing.assert_allclose(case._parameters['echo'].values, [0.0, 0.186289, 0.409836, 0.678092, 1.0], atol=1e-6, rtol=1e-6)
    assert case._parameters['foxtrot'].values == ['a', 'b', 'c']

    assert case._evaluables == {
        'dblalpha': '2 * alpha',
        'intasstring': '14',
        'floatasstring': '14.0',
    }

    assert case._pre_files[0].source == 'somefile'
    assert case._pre_files[0].target == 'somefile'
    assert case._pre_files[0].template
    assert case._pre_files[1].source == 'from'
    assert case._pre_files[1].target == 'to'
    assert case._pre_files[1].template
    assert case._pre_files[2].source == 'a'
    assert case._pre_files[2].target == 'b'
    assert not case._pre_files[2].template
    assert case._post_files[0].source == 'c'
    assert case._post_files[0].target == 'd'
    assert not case._post_files[0].template

    assert case._commands[0].command == 'string command here'
    assert case._commands[0].name == 'string'
    assert case._commands[0].capture_output == False
    assert case._commands[1].command == ['list', 'command', 'here']
    assert case._commands[1].name == 'list'
    assert case._commands[1].capture_output == False
    assert case._commands[2].command == '/usr/bin/nontrivial-name with args'
    assert case._commands[2].name == 'nontrivial-name'
    assert case._commands[2].capture_output == False
    assert case._commands[3].command == ['/usr/bin/nontrivial-name', 'with', 'args', 'as', 'list']
    assert case._commands[3].name == 'nontrivial-name'
    assert case._commands[3].capture_output == False
    assert case._commands[4].command == 'run this thing'
    assert case._commands[4].name == 'somecommand'
    assert case._commands[4].capture_output == True
    assert case._commands[5].command == '/some/nontrivial-stuff'
    assert case._commands[5].name == 'nontrivial-stuff'
    assert case._commands[5].capture_output == False

    assert case._logdir == 'loop-de-loop'
