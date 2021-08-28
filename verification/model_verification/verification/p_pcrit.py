import numpy as np
import matplotlib.pyplot as plt
from mpl_plotter.presets.panes import Lines


def cpr_air(nu_nozz):
    k = 1.4
    return 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))


def cpr_gas(nu_nozz):
    k = 1.33
    return 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))


x = np.linspace(0.2, 1, 100)
y = cpr_air(x)
z = cpr_gas(x)

plot = Lines().comparison
plot(x=[x, x], y=[y, z],
     colors=["blue", "red"], plot_labels=['$k_{air}$', '$k_{gas}$'],
     # Regular parameters
     title='Critical pressure ratio',
     x_label='$\mu_{nozzle}$',
     y_label='$p/p_{crit}$',
     y_label_pad=10,
     y_upper_bound=40,
     legend=False
     )
plt.gca().axhline(1, label='$p/p_{crit}$=1')
plt.legend()
plt.tight_layout()
plt.show()
