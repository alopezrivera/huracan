# Huracan

[The API reference is available here.](https://huracan-docs.github.io/)

**WARNING! Under active construction** :construction:

## Install

    pip install huracan
    
## Example script

Simple turbojet engine with 2 compressors and 2 turbines in a 2 shaft configuration and no secondary airflows.

    from huracan.engine import shaft
    from huracan.thermo.fluids import gas, fuel
    from huracan.components import intake, inlet, compressor, combustion_chamber, turbine, nozzle

    mf = 700
    m = 0.6
    t = 288
    p = 101325
    fr = 0

    fuel = fuel(LHV=43e6)

    g = gas(mf=mf,
            cp=lambda T: 1150 if T > 600 else 1000,
            k=lambda T: 1.33 if T > 600 else 1.4,
            m=m, t_0=t, p_0=p)

    i  = inlet(0.95)
    c  = compressor(0.9, 14)
    cc = combustion_chamber(fuel, 0.98)
    t  = turbine(0.9)

    shaft(c, t, eta=0.8)

    stream = g-i-c-cc-t
    
    stream.run()
    
    print(stream.t0())
    print(stream.p0())
