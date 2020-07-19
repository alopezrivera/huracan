import numpy as np
import matplotlib.pyplot as plt
from turbofan import Turbofan

from mpl_plotter.two_d import line
from mpl_plotter.two_d import scatter

tf = Turbofan()

tf.h = 15
tf.M = 0.85
tf.mf = 737
tf.bpr = 10
tf.T0_4 = 1750
tf.T_amb = 216.65
tf.p_amb = 22632

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
tf.correction(p=46564.319, t=270.6635)
tf.hmf()
tf.lpc('25')
tf.hpc('3')
tf.fmf()
tf.cc('4')
tf.work()
tf.hpt('45')
tf.correction(p=430438.833, t=1265.69645)
tf.lpt('5')
tf.nozzle_core('8')
tf.nozzle_bypass('18')
tf.exit_velocity()
tf.thrust_core()
tf.thrust_fan()

x, y = zip(*tf.record)
x, y = np.array(x), np.array(y)

line(x, y, color='grey', line_width=1,
     more_subplots_left=True, zorder=1, alpha=0.65)
scatter(ax=plt.gca(), fig=plt.gcf(), x=x, y=y, c=y,
        point_size=100, zorder=2, cmap='RdYlBu_r',
        x_tick_number=5, y_tick_number=5, title='Turbofan')


