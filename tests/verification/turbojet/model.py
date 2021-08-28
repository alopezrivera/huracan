from huracan.thermo.fluids import gas, fuel
from huracan.engine import shaft
from huracan.components import intake, inlet, compressor, combustion_chamber, turbine, nozzle


mf = 160
M = 0
t = 288
p = 101325

fuel = fuel(LHV=43e6)

g = gas(mf=mf,
        cp=lambda T: 1150 if T > 600 else 1000,
        k=lambda T: 1.33 if T > 600 else 1.4,
        m=M, t_0=t, p_0=p)

i  = inlet(PI=0.92)
c1 = compressor(eta=0.85, PI=4)
c2 = compressor(eta=0.85, PI=4)
cc = combustion_chamber(fuel, eta=0.97, t01=1450)
t1 = turbine(0.9)
t2 = turbine(0.9)

shaft1 = shaft(c1, t2, eta=0.99)
shaft2 = shaft(c2, t1, eta=0.99)

strm = g-i-c1-c2-cc-t1-t2  #-n

strm.run()

model_t0 = strm.t0()
model_p0 = strm.p0()

verification_t0 = [288.,
                   452.66630032,
                   711.48187307,
                   1450,
                   1227.1163336,
                   1085.31099956,
                   1850,
                   1587.98283262]
verification_p0 = [93219.,
                   372876.,
                   1491504.,
                   1446758.88,
                   680119.41922727,
                   390882.21425195,
                   379155.74782439,
                   197805.04920735]

# Compression verification
for i in range(verification_t0.index(1450)):
    assert model_t0[i] - verification_t0[i] < 10e-8, (i, model_t0[i], verification_t0[i])
    assert model_p0[i] - verification_p0[i] < 10e-8, (i, model_p0[i], verification_p0[i])
