# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from huracan.utils import setattr_namespace


class TestsFluid(unittest.TestCase):

    def test_setattr_namespace(self):
        class a:
            pass

        print(type(a))

        b = a()

        c = 1

        setattr_namespace(b, locals())

