# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))

"""
Turbojet engine test
--------------------
Twin-spool, reheated turbojet engine with an electrical power plant.
"""

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, compressor, combustion_chamber, turbine, afterburner, nozzle, electrical_system, bleed_duct

mf = 160
M  = 0
t  = 288
p  = 101325

fuel_cc = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=M, t_0=t, p_0=p)

"""
Define engine components
"""
i  = inlet             (PI=0.92)
c1 = compressor        (eta=0.85, PI=4); c1_bleed = 0.5 / 100
c2 = compressor        (eta=0.85, PI=4)
bd = bleed_duct        (t01=288.15, eta=0.95)
cc = combustion_chamber(fuel=fuel_cc, eta=0.97, t01=1450)
t1 = turbine           (eta=0.9)
t2 = turbine           (eta=0.9)
n  = nozzle            (eta=0.95)
elctr  = electrical_system(w=970000, eta_g=0.7, eta_c=0.98)

shaft1 = shaft(c1, t2,        eta=0.99)
shaft2 = shaft(c2, t1, elctr, eta=0.99)

"""
Define stream structure
"""
stream = g-i-c1

core_stream, compressor_bleed_stream = stream*c1_bleed

compressor_bleed_stream-bd

core_stream-c2-cc-t1-t2-n

# stream-c2-cc-t1-t2-n

"""
Simulate engine
"""
stream.run()

stream.plot(x='S', y='t0', show=True, colorblind=True)
stream.plot(x='V', y='p0', show=True, colorblind=True)
stream.plot(x='p0', y='H', show=True, colorblind=True)
stream.plot(x='p0', y='t0', show=True, colorblind=True)
