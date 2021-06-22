import numpy as np
from turboprop import Turboprop
from resources.utils_propulsion import cycle_graph

import matplotlib.pyplot as plt
from mpl_plotter.two_d import line, scatter

tp = Turboprop()

tp.M = 0.6
tp.mf = 35
tp.Pbr = hp(5250)
tp.T0_4 = 1130
tp.T_amb = 288.00
tp.p_amb = 101325.00

# pressure ratios
tp.pi_inlet = 1
tp.pi_C = 11.5
tp.pi_cc = 0.96

# isentropic efficiencies
tp.nu_prop = 0.9
tp.nu_C = 0.85
tp.nu_T = 0.89
tp.nu_mech = 0.99
tp.nu_cc = 0.995
tp.nu_nozzle = 0.95

# constants
tp.LHV = 43e6
tp.cp_air = 1000
tp.cp_gas = 1150
tp.k_air = 1.4
tp.k_gas = 1.33
tp.R = 287

tp.ambient()
tp.prop('1')
tp.inlet()
tp.comp('3')
tp.fmf()
tp.cc('4')
tp.work_exerted_monocomp()
tp.work_required_monoturb()
tp.turb('5')
tp.nozzle_core('8')
tp.exit_velocity()
tp.thrust_core()
tp.thrust_prop()
tp.sfc()

x, y = zip(*tp.record)
x, y = np.array(x), np.array(y)

line(x, y, figsize=(10, 5),
     color='black', line_width=2,
     zorder=3, alpha=0.85, label='Turboprop')
ax = plt.gca()
fig = plt.gcf()

from turbojet import Turbojet

tj = Turbojet()

tj.h = 0
tj.M = 0.6
tj.mf = 160
tj.T0_4 = 1450
tj.T0_7 = 1850
tj.T_amb = 288.00
tj.p_amb = 101325.00

# pressure ratios
tj.pi_inlet = 0.92
tj.pi_LPC = 4
tj.pi_HPC = 4
tj.pi_cc = 0.96
tj.pi_ab = 0.97

# isentropic efficiencies
tj.nu_inlet = 1.00
tj.nu_LPC = 0.85
tj.nu_HPC = 0.85
tj.nu_LPT = 0.9
tj.nu_HPT = 0.9
tj.nu_mech = 0.99
tj.nu_cc = 0.99
tj.nu_nozzle = 0.95
tj.nu_ab = 0.95

# constants
tj.LHV = 43e6
tj.cp_air = 1000
tj.cp_gas = 1150
tj.k_air = 1.4
tj.k_gas = 1.33
tj.R = 287

tj.ambient()
tj.inlet()
tj.lpc('25')
tj.hpc('3')
tj.fmf()
tj.cc('4')
tj.work_exerted()
tj.work_required()
tj.hpt('45')
tj.lpt('5')
tj.afterburner('7')
tj.nozzle_core('8')
tj.exit_velocity()
tj.thrust_core()
tj.abmf()
tj.sfc()

x, y = zip(*tj.record)
x, y = np.array(x), np.array(y)

line(x, y, ax=ax, fig=fig, color='darkred', line_width=2,
     more_subplots_left=True, zorder=2, alpha=0.85, label='Turbojet')

from turbofan import Turbofan

tf = Turbofan()

tf.h = 0
tf.M = 0.6
tf.mf = 737
tf.bpr = 10
tf.T0_4 = 1750
tf.T_amb = 288
tf.p_amb = 101325.00

# isentropic efficiencies
tf.nu_inlet = 0.97
tf.nu_fan = 0.85
tf.nu_LPC = 0.9
tf.nu_HPC = 0.87
tf.nu_LPT = 0.89
tf.nu_HPT = 0.89
tf.nu_mech = 0.99
tf.nu_cc = 0.99
tf.nu_nozzle = 0.98

# pressure ratios
tf.pi_fan = 1.3
tf.pi_LPC = 1.6
tf.pi_HPC = 27
tf.pi_cc = 0.96

# constants
tf.LHV = 43e6
tf.cp_air = 1000
tf.cp_gas = 1150
tf.k_air = 1.4
tf.k_gas = 1.33
tf.R = 287

tf.w_LPS = 2531

tf.ambient()
tf.inlet()
tf.fan('21')
tf.p0_21 = 46564.319
tf.hmf()
tf.lpc('25')
tf.hpc('3')
tf.fmf()
tf.cc('4')
tf.work_exerted()
tf.work_required()
tf.hpt('45')
tf.lpt('5')
tf.nozzle_core('8')
tf.nozzle_bypass('18')
tf.exit_velocity()
tf.thrust_core()
tf.thrust_fan()

x, y = zip(*tf.record)
x, y = np.array(x), np.array(y)

line(x, y, ax=ax, fig=fig, color='blue', line_width=2,
     zorder=1, alpha=0.85, label='Turbofan',
     title='Comparison\nSL M=0.6',
     x_label='S', x_tick_number=0,
     y_label='T [K]', y_label_pad=10, y_label_rotation=90, y_tick_number=10,
     legend=True,
     legend_loc=(0.75, 0.1),
     y_upper_bound=2000,
     # filename='comparison_0.1.png',
     # dpi=150
     )


plt.show()
