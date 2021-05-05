import numpy as np
from turboprop import Turboprop
from resources.utils_propulsion import cycle_graph, hp

tp = Turboprop()

tp.M = 0.5
tp.mf = 35
tp.Pbr = 3.91e6
tp.T0_4 = 1130
tp.T_amb = 288.15
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
tp.nu_comb = 0.995
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
tp.cc('4')
tp.fmf()
tp.work_exerted_monocomp('')
tp.work_required_monoturb()
tp.turb('5')
tp.pi_nozzle_core()
tp.nozzle_core('8')
tp.exit_velocity()
tp.nozzle_exit_area('8')
tp.thrust_core()
tp.thrust_prop()
tp.sfc()

x, y = zip(*tp.record)
x, y = np.array(x), np.array(y)

# cycle_graph(x, y, 'Turboprop')
