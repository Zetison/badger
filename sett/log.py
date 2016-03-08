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

stdout_verbosity = 1
log_verbosity = 3
log_file = None
past_first_run = False

REQUIRED_VERBOSITY = {
    'running': 1,
    'results': 1,
    'retcode': 1,
    'stderr': 2,
    'templates': 3,
    'stdout': 4,
}

def dispatch_log(string):
    with open(log_file, 'a') as f:
        f.write(string + '\n')

def dispatch_stdout(string):
    print(string)

def log(kind, string, title=None):
    global past_first_run

    if not string:
        return

    if kind in ['stderr', 'stdout', 'templates']:
        if string and string[-1] != '\n':
            string += '\n'
        start = ' ' + (title or kind) + ' '
        end = ' End of ' + (title or kind) + ' '
        string = '{:━^80}\n{}{:━^80}'.format(start, string, end)

    if kind == 'running':
        if past_first_run:
            string = '\n' + string
        past_first_run = True

    limit = REQUIRED_VERBOSITY[kind]

    if limit <= log_verbosity:
        dispatch_log(string)
    if limit <= stdout_verbosity:
        dispatch_stdout(string)
