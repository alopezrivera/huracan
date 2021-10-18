# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan
-------
Three-spool turbofan engine off-design analysis: thrust constraint.
"""

import time
import numpy as np
from scipy.optimize import minimize

from matmos import ISA

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, fan, compressor, combustion_chamber, turbine, nozzle


def engine(M, t, p,
           PI1, PI2):

    mf = 1440

    bpr = 9.6

    f = fuel(LHV=43e6)

    g = gas(mf=mf,
            cp=lambda T: 1150 if T > 1000 else 1000,
            k=lambda T: 1.33 if T > 1000 else 1.4,
            m=M, t_0=t, p_0=p)

    i  = inlet             (PI=0.98)
    fn = fan               (eta=0.94,  PI=1.54)
    c1 = compressor        (eta=0.991, PI=PI1)
    c2 = compressor        (eta=0.92,  PI=PI2)
    cc = combustion_chamber(fuel=f, eta=0.985, PI=0.99, t01=1838)
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

    stream.run(log=False)

    return stream.thrust_total(), stream.efficiency_total()


def opt(target_thrust,
        **kwargs):
    try:
        thrust, eff = engine(**kwargs)
        return (target_thrust - thrust) ** 2 / eff ** 4
    except AssertionError:
        return 10e20


# Flight conditions
M = 0.65

# Ambient conditions
h = 0
a = ISA(h)
t = a.t
p = a.p

# Conditions
target_thrust = 400000       # N

# Optimization
t0 = time.time()
PI1, PI2 = minimize(lambda x: opt(PI1=x[0], PI2=x[1],
                                  M=M, t=t, p=p,
                                  target_thrust=target_thrust),
                    x0=np.array([6, 3]),
                    ).x
print(f'Runtime: {time.time() - t0:.2f} s\n')

# Results
print(f'PI1    = {PI1:.2f}')
print(f'PI2    = {PI2:.2f}')

thrust, eff = engine(M=M, t=t, p=p, PI1=PI1, PI2=PI2)

print(f'T      = {thrust/1000:.2f} [kN]')
print(f'eta    = {eff:.3f}')
