"""
Huracan
-------
Three-spool turbofan engine test.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, fan, compressor, combustion_chamber, turbine, afterburner, nozzle, power_plant

from tests.utils import verify

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

"""
Verification

- Error must stay below 0.1% of the verification value 
"""
# Total temperature
verify(stream['0.il'].t0,    290.7)              # Inlet
verify(stream['0.fn'].t0,    331.3)              # Fan
verify(stream['1.m.nz'].t0,  287.2)              # Bypass flow nozzle
verify(stream['1.s.cp1'].t0, 635.1)              # Compressor 1
verify(stream['1.s.cp2'].t0, 922.4)              # Compressor 2

# Total pressure
verify(stream['0.il'].p0,    98343)              # Inlet
verify(stream['0.fn'].p0,    151447)             # Fan
verify(stream['1.m.nz'].p0,  89874)              # Bypass flow nozzle
verify(stream['1.s.cp1'].p0, 1455410)            # Compressor 1
verify(stream['1.s.cp2'].p0, 4919286)            # Compressor 2

# Heat and work
verify(fn.w, 58.46e6)                            # Work: Fan
verify(c1.w, 41.27e6)                            # Work: Compressor 1
verify(c2.w, 39.03e6)                            # Work: Compressor 2

"""
Exceptions:

The fuel mass flow method differs from
that used by the verification model. 
This causes differences in the models'
results after the main combustion chamber.

- Error must stay below 5% of the verification value 
"""
# Fuel mass flow
verify(cc.fuel.mf, 3.377, 0.05)

# Total temperature
verify(stream['1.s.tb1'].t0, 1593,    0.05)       # Turbine 1
verify(stream['1.s.tb2'].t0, 1334,    0.05)       # Turbine 2
verify(stream['1.s.tb3'].t0, 967,     0.05)       # Turbine 3

# Total pressure
verify(stream['1.s.tb1'].p0, 2666269, 0.05)       # Turbine 1
verify(stream['1.s.tb2'].p0, 1267264, 0.05)       # Turbine 2
verify(stream['1.s.tb3'].p0, 330414,  0.05)       # Turbine 3

# Thrust
verify(s1core._flow_thrust(), 85703, 0.1,
       True, 'e(T_core)')                         # Thrust

# Efficiency
verify(stream.sfc(), 11.36e-6, 0.1,
       True, 'e(SFC)')                            # Specific fuel consumption
