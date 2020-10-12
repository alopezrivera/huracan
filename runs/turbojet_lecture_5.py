import numpy as np
from turbojet import Turbojet
from resources.utils_propulsion import cycle_graph

tj = Turbojet()

tj.h = 0
tj.M = 0
tj.mf = 160
tj.T0_4 = 1450
tj.T0_7 = 1850
tj.T_amb = 288.00
tj.p_amb = 101325.00

# pressure ratios
tj.pi_inlet = 0.92
tj.pi_LPC = 4
tj.pi_HPC = 4
tj.pi_cc = 0.97
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
tj.cc('4')
tj.fmf()
tj.work_exerted()
tj.work_required()
tj.hpt('45')
tj.lpt('5')
tj.afterburner('7')
tj.abmf()
tj.pi_nozzle_core()
tj.nozzle_core('8')
tj.exit_velocity()
tj.nozzle_exit_area('8')
tj.thrust_core()
tj.sfc()

x, y = zip(*tj.record)
x, y = np.array(x), np.array(y)

# cycle_graph(x, y, 'Turbojet')


