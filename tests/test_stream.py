import unittest

from huracan.components import inlet, compressor, turbine, nozzle
from huracan.thermo.fluids import gas

mf = 700
m = 0.6
t = 288
p = 101325
fr = 0

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=m, t_0=t, p_0=p)


class TestsFluid(unittest.TestCase):

    def test_linear(self):
        i = inlet(0.95)
        c1 = compressor(0.95, 2)
        c2 = compressor(0.95, 14)

        c = g - i - c1 - c2

        c.run()

        assert c.s00.process.t0 == c.s01.process.t01        # Inlet - no change in total temperature
        assert c.s1.process.p01 == 2 * c.s01.process.p01    # Compressor 1
        assert c.s2.process.p01 == 14 * c.s1.process.p01    # Compressor 2
