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

import re
import shlex
import shutil

from os.path import join

from jinja2 import Template


class Command:

    def __init__(self, cmd, stdout=[], files=[]):
        self.args = [Template(a) for a in shlex.split(cmd)]
        self.stdout = [Template(s) for s in stdout]
        self.files = [Template(f) for f in files]

    def capture_stdout(self, stdout, namespace):
        results = {}
        for regexp in self.stdout:
            r = re.compile(regexp.render(**namespace), re.MULTILINE)
            matches = list(r.finditer(stdout))
            for m in matches:
                for g, v in m.groupdict().items():
                    results.setdefault(g, []).append(v)
        return results

    def capture_files(self, source, target, namespace):
        for fn in self.files:
            fn = fn.render(**namespace)
            shutil.copy(join(source, fn), join(target, fn))
