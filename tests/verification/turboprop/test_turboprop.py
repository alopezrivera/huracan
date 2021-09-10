# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0

"""
Huracan
-------
Single-spool turboprop engine test.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, prop, compressor, combustion_chamber, turbine, nozzle

from tests.utils import verify

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

"""
Verification

- Error must stay below 0.1% of the verification value 
"""
# Total temperature
verify(stream['0.il'].t0, 302.56)               # Inlet
verify(stream['0.cp'].t0, 661.84)               # Compressor

# Total pressure
verify(stream['0.il'].p0, 120192.99554985)      # Inlet
verify(stream['0.cp'].p0, 1382219.44882326)     # Compressor

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
verify(cc.fuel.mf, 0.4425,          error, log=True, name='e(fmf)')

# Total temperature
verify(stream['0.tb'].t0, 721.35,   error, log=True, name='e(tb.t0)')     # Turbine
verify(stream['0.nz'].t0, 645.8,    error, log=True, name='e(nz.t0)')     # Nozzle

# Total pressure
verify(stream['0.tb'].p0, 162.37e3, error, log=True, name='e(tb.p0)')     # Turbine
verify(stream['0.nz'].p0, 101325)                                         # Nozzle

# Exit velocity
verify(stream.v_exit(), 417.2,      error, log=True, name='e(v_exit)')

