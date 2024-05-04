# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[3]))

"""
Huracan
-------
Three-spool turbofan engine design condition analysis: performance at different altitudes.
"""

import time
import numpy as np
import matplotlib as mpl

from matmos import ISA
from mpl_plotter.two_d import panes

from huracan.engine import shaft
from huracan.thermo.fluids import gas, fuel
from huracan.components import inlet, fan, compressor, combustion_chamber, turbine, nozzle


def engine(M, t, p):

    mf = 1440

    bpr = 9.6

    f = fuel(LHV=43e6)

    g = gas(mf=mf,
            cp=lambda T: 1150 if T > 1000 else 1000,
            k=lambda T: 1.33 if T > 1000 else 1.4,
            m=M, t_0=t, p_0=p)

    i  = inlet             (PI=0.98)
    fn = fan               (eta=0.94,  PI=1.54)
    c1 = compressor        (eta=0.991, PI=9.61)
    c2 = compressor        (eta=0.92,  PI=3.38)
    cc = combustion_chamber(fuel=f, eta=0.985, PI=0.99, t01=1838)
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

    stream.run(log=False)

    return stream.thrust_total(), stream.efficiency_total()


# Setup
n = 100
m = 10

# Flight conditions
M = np.linspace(0.2, 0.7, n)

# Atmospheric conditions
h = np.linspace(0, 12, m)
a = ISA(h)
t = a.t
p = a.p

thrust = []
eff    = []

t0 = time.time()
for i in range(n):
    _thrust = np.zeros(m)
    _eff    = np.zeros(m)
    for j in range(m):
        _thrust[j], _eff[j] = engine(M=M[i], t=t[j], p=p[j])
    thrust.append(_thrust/1000)
    eff.append(_eff)
print(f'Runtime: {time.time()-t0:.2f} s')

cmap = mpl.cm.get_cmap('RdBu')

panes([thrust, eff],
      h,
      labels_x=['T [kN]', '$\eta_T$'],
      label_y='h [km]',
      colors=[cmap(Mi) for Mi in M],
      line_width=2,
      top=0.95,
      bottom=0.17,
      left=0.1,
      right=0.85,
      hspace=0.35,
      wspace=0.6,
      )

# Colorbar
from matplotlib import pyplot as plt

cb_max = M.max()
cb_min = M.min()

cax = plt.gcf().add_axes([0.9, 0.205,
                          0.015,  0.7])

cb = mpl.colorbar.ColorbarBase(ax=cax,
                               cmap=cmap,
                               norm=mpl.colors.BoundaryNorm(np.linspace(cb_min, cb_max, 256).tolist(), cmap.N),
                               boundaries=np.linspace(cb_min, cb_max, 256).tolist(),
                               extendfrac='auto',
                               ticks=[round(v, 2) for v in np.linspace(cb_min, cb_max, 5)],
                               spacing='uniform',
                               orientation='vertical')

cb.ax.set_title(f'M', pad=10)

plt.show()
