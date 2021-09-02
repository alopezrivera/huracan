import numpy as np
from tests.verification.model_verification.turbofan import Turbofan
from tests.verification.model_verification.resources.utils_propulsion import cycle_graph

tf = Turbofan()

tf.h = 1000
tf.M = 0.4
tf.mf = 1440
tf.bpr = 9.6
tf.T_amb = 281.65
tf.p_amb = 89874

# pressure ratios
tf.pi_inlet = 0.98
tf.pi_fan = 1.54
tf.pi_LPC = 1.54
tf.pi_HPC = 9.61
tf.pi_cc = 0.98

# isentropic efficiencies
tf.nu_fan = 0.92
tf.nu_LPC = 0.89
tf.nu_HPC = 0.89
tf.nu_HPT = 0.89
tf.nu_LPT = 0.89
tf.nu_cc = 0.965

# nozzle efficiencies
tf.nu_nozzle_core = 0.96
tf.nu_nozzle_bypass = 0.95

# mechanical efficiencies
tf.nu_mech = 0.98
tf.nu_gearbox = 0.975

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
tf.work_exerted()
tf.work_required()
tf.cc('w_given', '4')
tf.fmf()
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



