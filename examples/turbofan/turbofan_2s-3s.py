# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan
-------
Three-spool turbofan engine.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, fan, compressor, combustion_chamber, turbine, nozzle

mf = 1440
M  = 0.4
t  = 281.65
p  = 89874

bpr = 9.6

fuel = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 1000 else 1000,
        k=lambda T: 1.33 if T > 1000 else 1.4,
        m=M, t_0=t, p_0=p)

i  = inlet             (PI=0.98)
fn = fan               (eta=0.94,  PI=1.54)
c1 = compressor        (eta=0.991, PI=9.61)
c2 = compressor        (eta=0.92,  PI=3.38)
cc = combustion_chamber(fuel=fuel, eta=0.985, PI=0.99, t01=1838)
t1 = turbine           (eta=0.96)
t2 = turbine           (eta=0.965)
t3 = turbine           (eta=0.97)
nc = nozzle            (eta=0.95)
nf = nozzle            (eta=0.96)

shaft1 = shaft(fn, t3, eta=0.995)
shaft2 = shaft(c1, t2, eta=0.995)
shaft3 = shaft(c2, t1, eta=0.995)

stream = g-i-fn

s1core, s1bypass = stream*(bpr/(bpr+1))

s1core-c1-c2-cc-t1-t2-t3-nc
s1bypass-nf

stream.run()

stream.plot_T_S(show=True, legend=True)
stream.plot_p_V(show=True, legend=True)
stream.plot_p_H(show=True, legend=True)
stream.plot_T_p(show=True, legend=True)
