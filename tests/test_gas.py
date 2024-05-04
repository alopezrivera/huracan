# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

# Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))

# General imports
import unittest

# Huracan
from huracan.thermo.fluids import gas, fuel

mf = 700
m  = 0.6
t  = 288
p  = 101325
fr = 0.1

g = gas(mf = mf,
        cp = lambda T: 1150 if T > 600 else 1000,
        k  = lambda T: 1.33 if T > 600 else 1.4,
        m  = m, t_0=t, p_0=p)

f = gas(mf = mf,
        cp = lambda T: 1150 if T > 600 else 1000,
        k  = lambda T: 1.33 if T > 600 else 1.4,
        m  = m, t_0=t*fr, p_0=p*fr)

k = gas(mf = mf,
        cp = lambda T: 1500 if T > 1000 else 1200 if T > 800 else 400,
        k  = lambda T: 1.33 if T > 600 else 1.4,
        m  = m, t_0=t*fr, p_0=p*fr)


class TestsFluid(unittest.TestCase):

    def test_mixture(self):
        global h
        h = g+f

        assert abs(h.t0 - g.t0/2) < 10e-12
        assert abs(h.p0 - g.p0/2) < 10e-12

    def test_diversion(self):
        mf = h.mf
        fr = 0.2
        i, j = fr*h

        assert i.mf == mf*(1-fr)
        assert j.mf == mf*fr
