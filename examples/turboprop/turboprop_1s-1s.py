# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan
-------

Two-spool turboprop engine.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, prop, compressor, combustion_chamber, turbine, nozzle

mf = 35
M  = 0.5
t  = 288.15
p  = 101325.00

fuel = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=M, t_0=t, p_0=p)

pr = prop(eta=0.9, w=3.91e6, PI=1)
i  = inlet(PI=1)
c  = compressor(eta=0.85, PI=11.5)
cc = combustion_chamber(fuel=fuel, eta=0.995, t01=1130, PI=0.96)
t  = turbine(eta=0.89)
n  = nozzle(eta=0.95)

shaft1 = shaft(pr, c, t, eta=0.99)

stream = g-pr-i-c-cc-t-n

stream.run()

stream.plot_T_S(show=True, color='purple')
stream.plot_p_V(show=True, color='orange')
stream.plot_p_H(show=True, color='purple')
stream.plot_T_p(show=True, color='orange')
