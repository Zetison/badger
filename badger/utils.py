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
# License along with BADGER. If not, see
# <http://www.gnu.org/licenses/>.
#
# In accordance with Section 7(b) of the GNU Affero General Public
# License, a covered work must retain the producer line in every data
# file that is created or manipulated using BADGER.
#
# Other Usage
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as you
# develop commercial activities involving BADGER without disclosing the
# source code of your own applications.
#
# This file may be used in accordance with the terms contained in a
# written agreement between you and SINTEF ICT.

import subprocess
from os.path import exists, dirname
from os import makedirs


def coerce_list(value, split=None, required=False):
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        if isinstance(split, str):
            return value.split(split)
        elif split:
            return split(value)
    return [value]


def coerce_types(dictionary, types):
    type_map = {'float': float, 'str': str, 'int': int, 'bool': bool}
    for key, val in dictionary.items():
        if key in types:
            tp = types[key]
            if isinstance(tp, str):
                dictionary[key] = type_map[tp](val[-1])
            elif isinstance(tp, list):
                func = type_map[tp[0]]
                dictionary[key] = [func(v) for v in val]


def run_process(args, path):
    p = subprocess.Popen(args, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    return stdout, stderr, p.returncode


def ensure_path_exists(filename, file=True):
    if file:
        filename = dirname(filename)
    if filename and not exists(filename):
        makedirs(filename)
