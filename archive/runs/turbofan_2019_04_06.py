import numpy as np
from turbofan import Turbofan
from resources.utils_propulsion import cycle_graph

tf = Turbofan()

tf.h = 15
tf.M = 0.85
tf.mf = 737
tf.bpr = 10
tf.T0_4 = 1750
tf.T_amb = 216.65
tf.p_amb = 22632

# pressure ratios
tf.pi_fan = 1.3
tf.pi_LPC = 1.6
tf.pi_HPC = 27
tf.pi_cc = 0.96

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
tf.hmf()
tf.lpc('25')
tf.hpc('3')
tf.cc('t_given', '4')
tf.fmf()
tf.work_exerted()
tf.work_required()
tf.hpt('45')
tf.lpt('5')
tf.pi_nozzle_core()
tf.pi_nozzle_bypass()
tf.nozzle_core('8')
tf.nozzle_bypass('18')
tf.exit_velocity()
tf.nozzle_exit_area('8')
tf.thrust_core()
tf.thrust_fan()

x, y = zip(*tf.record)
x, y = np.array(x), np.array(y)

cycle_graph(x, y, 'Turbofan')



