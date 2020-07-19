from resources.propulsion import *
from resources.functions_turbofan import *


class Turbofan:

    def __init__(self):
        self.h = None
        self.M = None
        self.mf = None
        self.bpr = None
        self.T0_4 = None
        self.T_amb = None
        self.p_amb = None

        # isentropic efficiencies
        self.nu_inlet = None
        self.nu_fan = None
        self.nu_LPC = None
        self.nu_HPC = None
        self.nu_LPT = None
        self.nu_HPT = None
        self.nu_mech = None
        self.nu_cc = None
        self.nu_nozzle = None

        # pressure ratios
        self.pi_fan = None
        self.pi_LPC = None
        self.pi_HPC = None
        self.pi_cc = None

        # constants
        self.LHV = 43e6
        self.cp_air = 1000
        self.cp_gas = 1150
        self.k_air = 1.4
        self.k_gas = 1.33
        self.R = 287

        self.w_LPS = None

    def ambient(self):
        self.p, self.t = self.p_amb, self.T_amb
        self.record = [[self.p, self.t]]

    def inlet(self):
        self.p0_0, self.t0_0 = inlet(pamb=self.p_amb, tamb=self.T_amb, m=self.M, k=self.k_air, pi=1, nu=self.nu_inlet)

        self.method_record(self.p0_0, self.t0_0)

    def lpc(self, stage):
        self.p0_25, self.t0_25 = compressor(pbc=self.p, tbc=self.t, k=self.k_air, pi=self.pi_LPC, nu=self.nu_LPC,
                                            stage=stage, kind='LPC')

        self.method_record(self.p0_25, self.t0_25)

    def hpc(self, stage):
        self.p0_3, self.t0_3 = compressor(pbc=self.p, tbc=self.t, k=self.k_air, pi=self.pi_HPC, nu=self.nu_HPC,
                                          stage=stage, kind='HPC')

        self.method_record(self.p0_3, self.t0_3)

    def fmf(self):
        fuel_mass_flow(tbc=self.t, tac=self.T0_4, mf=self.hmf, cp=self.cp_gas, nu=self.nu_cc, lhv=self.LHV)

    def cc(self, stage):
        self.p0_4, self.t0_4 = cc_pressure(pbcc=self.p, tacc=self.T0_4, pi=self.pi_cc,
                                           stage=stage)

        self.method_record(self.p0_4, self.t0_4)

    def work(self):
        self.w_comp1 = compr_work(self.mf, self.cp_air, self.t0_21, self.t0_25, 'LPC')
        self.w_comp2 = compr_work(self.mf, self.cp_air, self.t0_25, self.t0_3, 'HPC')
        self.w_fan = fan_power(self.t0_0, self.t0_21, self.mf, self.cp_air, self.nu_mech, None)

    def hpt(self, stage):
        self.p0_45, self.t0_45 = turbine(w=self.w_comp2, mf=self.hmf, cp=self.cp_gas, k=self.k_gas, nu=self.nu_HPT, tbt=self.t, pbt=self.p,
                                         stage=stage, kind='HPT')

        self.method_record(self.p0_45, self.t0_45)

    def lpt(self, stage):

        self.p0_5, self.t0_5 = turbine(w=self.w_comp1 + self.w_fan, mf=self.hmf, cp=self.cp_gas, k=self.k_gas, nu=self.nu_LPT, tbt=self.t, pbt=self.p,
                                       stage=stage, kind='LTP')

        self.method_record(self.p0_5, self.t0_5)

    def nozzle_core(self, stage):
        print_color('Core flow', 'green')
        self.p_pc_nozzle = is_nozzle_choked(self.nu_nozzle, self.k_gas)

        self.p0_8, self.t0_8 = choked_nozzle(self.p, self.t, self.p_pc_nozzle, self.k_gas, self.nu_nozzle,
                                             stage=stage)

        self.method_record(self.p0_8, self.t0_8)

    def exit_velocity(self):
        self.v8 = exit_velocity(self.k_gas, self.R, self.t0_8, 'Core')
        self.v0 = v0(self.k_air, self.R, self.T_amb, self.M)

    def thrust(self):
        self.T_core = flow_thrust(self.hmf, self.v8, self.v0, which='Core')

    def method_record(self, p, t):
        self.p = p
        self.t = t
        self.record.append([self.p, self.t])

    def correction(self, p, t):
        self.p = p
        self.t = t
