from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, fan, compressor, combustion_chamber, turbine, afterburner, nozzle, power_plant

mf = 1440
M  = 0.4
t  = 281.65
p  = 89874

bpr = 9.6

fuel = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=M, t_0=t, p_0=p)

i  = inlet             (PI=0.98)
fn = fan               (eta=0.92, PI=1.54, bpr=bpr)
c1 = compressor        (eta=0.89, PI=1.54)
c2 = compressor        (eta=0.89, PI=9.61)
cc = combustion_chamber(fuel=fuel, eta=0.965, PI=0.98)
t1 = turbine           (eta=0.89)
t2 = turbine           (eta=0.89)
n  = nozzle            (eta=1)

shaft1 = shaft(fn, c1, t2, eta=0.98, eta_gearbox=0.975)
shaft2 = shaft(c2, t1, eta=0.98)

stream = g-i-fn

s2, s3 = stream*(bpr/(bpr+1))

s2-c1-c2-cc-t1-t2

s4 = s2-s3

s4-n

stream.run()

# stream.plot_T_p(show=True, color='purple')
# stream.plot_p_v(show=True, color='orange')
