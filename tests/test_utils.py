# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

# Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))

# General imports
import unittest

# Huracan
from huracan.utils import setattr_namespace


class TestsFluid(unittest.TestCase):

    def test_setattr_namespace(self):
        class a:
            pass

        print(type(a))

        b = a()

        c = 1

        setattr_namespace(b, locals())

