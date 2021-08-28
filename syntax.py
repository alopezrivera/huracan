from huracan.thermo.gas import gas, fuel
from placeholder_str import shaft
from placeholder_comp import inlet, compressor, combustion_chamber, turbine
from placeholder_mods import recuperator, afterburner


# Gas
g = gas(t_0 = 280,
        p_0 = 100000,
        mf = 1340,
        m = 0.65,
        cp = lambda T: 1150 if T > 600 else 1000,
        k  = lambda T: 1.4  if T > 600 else 1.3)

f = fuel(mf=20,
         LHV=43e6)

# Components
inlet              = inlet()
compressor1        = compressor()
compressor2        = compressor()
combustion_chamber = combustion_chamber()
turbine1           = turbine()
turbine2           = turbine()
# Modifiers
recuperator        = recuperator()
afterburner        = afterburner()

# Engine geometry
shaft1 = shaft(compressor1, turbine1)
shaft2 = shaft(compressor2, turbine2)

free_power_shaft = shaft(turbine2)

# Engine cycle
c = inlet-compressor1-compressor2-combustion_chamber-turbine1-turbine2-afterburner -> cycle object

c.inlet-intercooler-c.compressor2 -> cycle object

c.turbine-recuperator-c.compressor2

engine.cycle(c)

# Simulate
engine.run()
