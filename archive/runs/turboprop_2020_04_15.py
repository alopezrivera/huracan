import numpy as np
from turboprop import Turboprop
from resources.utils_propulsion import cycle_graph

tp = Turboprop()

tp.M = 0.5
tp.mf = 5.3
tp.Pbr = 890e3
tp.T0_45 = 1050
tp.T_amb = 249.15
tp.p_amb = 47174.359378

# pressure ratios
tp.pi_inlet = 0.95
tp.pi_C = 8
tp.pi_cc = 0.96

# isentropic efficiencies
tp.nu_prop = 0.9
tp.nu_inlet = 0.98
tp.nu_C = 0.88
tp.nu_LPT = 0.93
tp.nu_HPT = 0.91
tp.nu_mech = 0.99
tp.nu_gearbox = 0.95
tp.nu_cc = 0.99
tp.nu_nozzle = 0.97

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
tp.work_exerted_monocomp('HPC')
tp.cc('4', 'interturbine')
tp.fmf()
tp.work_required_biturb()
tp.hpt('45')
tp.lpt('5')
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
