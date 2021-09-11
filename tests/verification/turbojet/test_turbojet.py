# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan
-------
Twin-spool, reheated turbojet engine test.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, compressor, combustion_chamber, turbine, afterburner, nozzle

from tests.utils import verify

mf = 160
M  = 0
t  = 288
p  = 101325

fuel_cc = fuel(LHV=43e6)
fuel_ab = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=M, t_0=t, p_0=p)

i  = inlet(PI=0.92)
c1 = compressor(eta=0.85, PI=4)
c2 = compressor(eta=0.85, PI=4)
cc = combustion_chamber(fuel_cc, eta=0.97, t01=1450)
t1 = turbine(0.9)
t2 = turbine(0.9)
ab = afterburner(fuel_ab, eta=0.95, t01=1850)
n  = nozzle(0.95)

shaft1 = shaft(c1, t2, eta=0.99)
shaft2 = shaft(c2, t1, eta=0.99)

stream = g-i-c1-c2-cc-t1-t2-ab-n

stream.run()

"""
Verification

- Error must stay below 0.1% of the verification value 
"""
# Total temperature
verify(stream['0.il'].t0,    288)               # Inlet
verify(stream['0.cp1'].t0, 452.66630032)      # Compressor 1
verify(stream['0.cp2'].t0, 711.48187307)      # Compressor 2

# Total pressure
verify(stream['0.il'].p0,    93219)             # Inlet
verify(stream['0.cp1'].p0, 372876)           # Compressor 1
verify(stream['0.cp2'].p0, 1491504)           # Compressor 2

"""
Exceptions:

The fuel mass flow method differs from
that used by the verification model. 
This causes differences in the models'
results after the main combustion chamber.

- Error must stay below 5% of the verification value 
"""

error = 0.05

# Fuel mass flow
verify(cc.fuel.mf, 3.1921,                  error, log=True, name='e(fmf)')

# Total temperature
verify(stream['0.tb1'].t0, 1227.1163336,    error, log=True, name='e(tb1.t0)')  # Turbine 1
verify(stream['0.tb2'].t0, 1085.31099956,   error, log=True, name='e(tb2.t0)')  # Turbine 2

# Total pressure
verify(stream['0.tb1'].p0, 680119.41922727, error, log=True, name='e(tb1.p0)')  # Turbine 1
verify(stream['0.tb2'].p0, 390882.21425195, error, log=True, name='e(tb2.p0)')  # Turbine 2

# Exit velocity
verify(stream.v_exit(), 840.3353,           error, log=True, name='e(v_exit)')
