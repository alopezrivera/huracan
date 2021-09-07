"""
Huracan
-------

Two-spool, reheated turbojet engine.

- 2 compressors
- 2 turbines
- Electrical power plant

"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, compressor, combustion_chamber, turbine, afterburner, nozzle, power_plant

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

i  = inlet             (PI=0.92)
c1 = compressor        (eta=0.85, PI=4)
c2 = compressor        (eta=0.85, PI=4)
cc = combustion_chamber(fuel=fuel_cc, eta=0.97, t01=1450)
t1 = turbine           (eta=0.9)
t2 = turbine           (eta=0.9)
ab = afterburner       (fuel=fuel_ab, eta=0.95, t01=1850)
n  = nozzle            (eta=0.95)

p  = power_plant(w=970000, eta_g=0.7, eta_c=0.98)

shaft1 = shaft(c1, t2,    eta=0.99)
shaft2 = shaft(c2, t1, p, eta=0.99)

stream = g-i-c1-c2-cc-t1-t2-ab-n

stream.run()

stream.plot_T_p(show=True, color='purple')
stream.plot_p_V(show=True, color='orange')

print(stream.v_exit())
print(stream.A_exit())
print(stream.flow_thrust())
