import numpy as np
from turbofan_ic_r import Turbofan
from resources.utils_propulsion import cycle_graph

tf = Turbofan()

tf.M = 0.8
tf.mf = 1150
tf.bpr = 9
tf.T0_4 = 2000
tf.T_amb = 219
tf.p_amb = 23842

# Intercooler and recuperator
tf.taic_core = 400
tf.taic_bp = 320
tf.rec_dt = 300

tf.E_intercooler = 0.77
tf.E_recuperator = 0.9

tf.pi_intercooler = 0.96
tf.pi_recuperator_comp = 0.94
tf.pi_recuperator_nozz = 0.96

# pressure ratios
tf.pi_fan = 1.5
tf.pi_LPC = 7
tf.pi_HPC = 9
tf.pi_cc = 0.96

# isentropic efficiencies
tf.nu_inlet = 0.98
tf.nu_fan = 0.93
tf.nu_LPC = 0.92
tf.nu_HPC = 0.91
tf.nu_LPT = 0.93
tf.nu_HPT = 0.92
tf.nu_mech = 0.99
tf.nu_gearbox = 0.95
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
tf.lpc('22')
tf.intercooler('23')
tf.hpc('24')
tf.recuperator_heat('3')
tf.cc('t_given', '4')
tf.fmf()
tf.work_exerted()
tf.work_required()
tf.hpt('45')
tf.lpt('5')
tf.recuperator_remove('7')
tf.pi_nozzle_core()
tf.pi_nozzle_bypass()
tf.nozzle_core('8')
tf.nozzle_bypass('18')
tf.exit_velocity()
tf.nozzle_exit_area('8')
tf.thrust_core()
tf.thrust_fan()
tf.sfc()

x, y = zip(*tf.record)
x, y = np.array(x), np.array(y)

cycle_graph(x, y, 'Turbofan')



