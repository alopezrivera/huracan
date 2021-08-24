from src.components import inlet, compressor, turbine, nozzle
from src.thermo.gas import gas


if __name__ == '__main__':

    mf = 700
    m = 0.6
    t = 288
    p = 101325
    fr = 0

    g = gas(mf=mf,
            cp=lambda T: 1150 if T > 600 else 1000,
            k=lambda T: 1.33 if T > 600 else 1.4,
            m=m, t_0=t, p_0=p)

    i  = inlet(0.95)
    c1 = compressor(0.95, 2)
    c2 = compressor(0.95, 14)

    c = g-i-c1-c2
