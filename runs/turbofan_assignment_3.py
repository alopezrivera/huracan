import numpy as np
from turbofan import Turbofan
from resources.utils_propulsion import cycle_graph

tf = Turbofan()

tf.h = None
tf.M = 0.73
tf.mf = 298
tf.bpr = 5.5
tf.dT0_4 = 650
tf.T_amb = 219
tf.p_amb = 23842

# pressure ratios
tf.pi_fan = 1.6
tf.pi_LPC = 1.35
tf.pi_HPC = 11
tf.pi_cc = 0.96

# isentropic efficiencies
tf.nu_inlet = 0.97
tf.nu_fan = 0.93
tf.nu_LPC = 0.91
tf.nu_HPC = 0.88
tf.nu_HPT = 0.89
tf.nu_LPT = 0.9
tf.nu_cc = 0.985

# nozzle efficiencies
tf.nu_nozzle = 0.98

# mechanical efficiencies
tf.nu_mech = 0.99

# constants
tf.LHV = 43e6
tf.cp_air = 1000
tf.cp_gas = 1150
tf.k_air = 1.4
tf.k_gas = 1.33
tf.R = 287

tf.ambient()
tf.inlet()
tf.fan('21')
tf.hmf()
tf.lpc('25')
tf.hpc('3')
tf.cc('dt_given', '4')
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
