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

from yaml import dump as yaml_dump


FORMATS = ['yaml', 'py']


def yaml(data, types, fn):
    with open(fn, 'w') as f:
        yaml_dump(data, f, default_flow_style=False)


def py(data, types, fn):
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
