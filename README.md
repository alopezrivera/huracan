# Huracan

[The API reference is available here.](https://huracan-docs.github.io/)

## Install

    pip install huracan
    
## Example script

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

    shft = shaft(c, t, eta=0.8)

    def r_stream_gas_input():
        strm   = i-c     ;    strm(g).run()
        strm_g = g-i-c   ;    strm_g.run()

    strm = g-i-c-cc-t
    
    strm.run()
    
    print(strm.t0())
    print(strm.p0())
