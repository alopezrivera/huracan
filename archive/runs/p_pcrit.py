import numpy as np
import matplotlib.pyplot as plt
from mpl_plotter.two_d import line


def cpr_air(nu_nozz):
    k = 1.4
    return 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))


def cpr_gas(nu_nozz):
    k = 1.33
    return 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))


x = np.linspace(0.2, 1, 100)
y = list(map(cpr_air, x))
z = list(map(cpr_gas, x))

line(x=x, y=y, label='$k_{air}$', color='blue', more_subplots_left=True)
line(x=x, y=z, label='$k_{gas}$', color='red', more_subplots_left=True, ax=plt.gca(), fig=plt.gcf(),
     title='Critical pressure ratio',
     x_label='$\mu_{nozzle}$',
     y_label='$p/p_{crit}$',
     y_label_pad=25,
     y_upper_bound=40,
     )
plt.gca().axhline(1, label='$p/p_{crit}$=1')
plt.legend()
plt.tight_layout()
plt.show()
