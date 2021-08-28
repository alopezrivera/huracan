import unittest

from huracan.thermo.gas import gas

mf = 700
m = 0.6

t = 288
p = 101325

fr = 0

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=m, t_0=t, p_0=p)

f = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=m, t_0=t * fr, p_0=p * fr)


class TestsFluid(unittest.TestCase):

    def test_gas(self):
        g = gas(1450,
                lambda T: 1150 if T > 600 else 1000,
                lambda T: 1.33 if T > 600 else 1.4)
        a = g.absolute(0.6, 288, 101325)
        b = g.diffusion(0.9, 0.8, 300, 121325)
        c = g.compression(0.85, 450, 200000, PI=14)
        d = g.expansion(0.85, 893.9732886318843, 2800000, TAU=0.3)

    def test_fuel(self):
        f = fuel(10, 43e6)

    def test_diversion(self):
        mf = 1450
        fr = 0.2

        g = gas(mf,
                lambda T: 1150 if T > 600 else 1000,
                lambda T: 1.33 if T > 600 else 1.4)

        g, gg = g * fr

        assert g.mf == mf * (1 - fr)
        assert gg.mf == mf * fr