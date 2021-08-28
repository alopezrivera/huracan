from verification.model_verification.resources.functions_propulsion import *
from verification.model_verification.resources.functions_turbojet import *


class Turbojet:

    def __init__(self):
        self.h = None
        self.M = None
        self.mf = None
        self.T0_4 = None
        self.T0_45 = None
        self.dT0_4 = None
        self.T0_7 = None
        self.T_amb = None
        self.p_amb = None

        # pressure ratios
        self.pi_LPC = None
        self.pi_HPC = None
        self.pi_cc = None
        self.pi_inlet = 1
        self.pi_ab = None
        # self.pi_nozzle_core = None

        # isentropic efficiencies
        self.nu_inlet = 1
        self.nu_LPC = None
        self.nu_HPC = None
        self.nu_LPT = None
        self.nu_HPT = None
        self.nu_cc = None
        self.nu_comb = None
        self.nu_ab = None

        # nozzle efficiencies
        self.nu_nozzle = None
        self.nu_nozzle_core = None

        # mechanical efficiencies
        self.nu_mech = None
        self.nu_mech_LP = None
        self.nu_mech_HP = None
        self.nu_gearbox = None

        # constants
        self.LHV = 43e6
        self.cp_air = 1000
        self.cp_gas = 1150
        self.k_air = 1.4
        self.k_gas = 1.33
        self.R = 287

        self.w_LPS = None

    def efficiencies(self):
        # nozzle efficiencies
        self.nu_nozzle_core = self.nu_nozzle if isinstance(self.nu_nozzle_core, type(None)) else self.nu_nozzle_core

        # combustion chamber efficiency
        if not isinstance(self.nu_comb, type(None)):
            self.nu_cc = self.nu_cc * self.nu_comb
        elif isinstance(self.nu_cc, type(None)):
            self.nu_cc = self.nu_comb

        # mechanical efficiencies
        if isinstance(self.nu_mech_LP, type(None)):
            self.nu_mech_LP = self.nu_mech

        if isinstance(self.nu_mech_HP, type(None)):
            self.nu_mech_HP = self.nu_mech

    def ambient(self):
        # initialize efficiencies
        self.efficiencies()
        # initialize p, t
        self.p, self.t = self.p_amb, self.T_amb
        self.record = [[self.p, self.t]]

        self.p0_0, self.t0_0 = ambient(self.p, self.t, self.M, self.k_air)

        self.method_record(self.p0_0, self.t0_0)

    def inlet(self):
        self.p0_2, self.t0_2 = inlet(self.p_amb, self.T_amb, self.M, self.k_air, self.pi_inlet, self.nu_inlet)

        self.method_record(self.p0_2, self.t0_2)

    def lpc(self, stage):
        self.p0_25, self.t0_25 = compressor(pbc=self.p, tbc=self.t, k=self.k_air, pi=self.pi_LPC, nu=self.nu_LPC,
                                            stage=stage, kind='LPC')

        self.method_record(self.p0_25, self.t0_25)

    def hpc(self, stage):
        self.p0_3, self.t0_3 = compressor(pbc=self.p, tbc=self.t, k=self.k_air, pi=self.pi_HPC, nu=self.nu_HPC,
                                          stage=stage, kind='HPC')

        self.method_record(self.p0_3, self.t0_3)

    def fmf(self):
        self.fmf = fuel_mass_flow(tbc=self.t0_3, tac=self.T0_4, mf=self.mf, cp=self.cp_gas, nu=0.99, lhv=self.LHV)

    def cc(self, stage, kind='t_given'):
        if kind == 't_given':
            self.p0_4, self.t0_4 = cc_t_given(pbcc=self.p, tacc=self.T0_4, pi=self.pi_cc,
                                              stage=stage)
        if kind == 'dt_given':
            self.p0_4, self.t0_4 = cc_dt_given(pbcc=self.p, tbcc=self.t, dt=self.dT0_4, pi=self.pi_cc,
                                               stage=stage)
        if kind == 'fmf_given':
            self.p0_4, self.t0_4 = cc_fmf_given(pbcc=self.p, tbcc=self.t, pi=self.pi_cc, mf=self.mf, fmf=self.fmf,
                                                nu=self.nu_cc, cp=self.cp_gas, LHV=self.LHV, stage=stage)
        if kind == 'w_given':
            self.p0_4, self.t0_4 = cc_w_given(pbcc=self.p, tbcc=self.t, pi=self.pi_cc, w_HPT=self.w_HPT,
                                              w_LPT=self.w_LPT,
                                              mf=self.mf, cp=self.cp_gas, nu=self.nu_cc, stage=stage)
        if kind == 'interturbine':
            self.p0_4, self.t0_4 = cc_t_interturbine(self.p, self.T0_45, self.pi_cc, self.w_HPC, self.mf,
                                                     self.cp_gas, self.nu_cc, stage)

        self.method_record(self.p0_4, self.t0_4)

    def work_exerted(self):
        self.w_LPC = compr_work(self.mf, self.cp_air, self.t0_2, self.t0_25, 'LPC')
        self.w_HPC = compr_work(self.mf, self.cp_air, self.t0_25, self.t0_3, 'HPC')

    def work_required(self):
        self.w_HPT = turbine_pr(self.w_HPC, self.nu_mech_HP)
        self.w_LPT = turbine_pr(self.w_LPC, self.nu_mech_LP)

    def hpt(self, stage):
        self.p0_45, self.t0_45 = turbine(w=self.w_HPT, mf=self.mf+self.fmf, cp=self.cp_gas, k=self.k_gas, nu=self.nu_HPT, tbt=self.t, pbt=self.p,
                                         stage=stage, kind='HPT')

        self.method_record(self.p0_45, self.t0_45)

    def lpt(self, stage):
        self.p0_5, self.t0_5 = turbine(w=self.w_LPT, mf=self.mf+self.fmf, cp=self.cp_gas, k=self.k_gas, nu=self.nu_LPT, tbt=self.t, pbt=self.p,
                                       stage=stage, kind='LPT')

        self.method_record(self.p0_5, self.t0_5)

    def afterburner(self, stage):
        if isinstance(self.T0_7, type(None)):
            self.p0_7, self.t0_7 = afterburner(self.p, self.p, self.k_gas, self.pi_ab, self.nu_ab, stage)
        else:
            self.p0_7, self.t0_7 = afterburner_t_given(self.p, self.T0_7, self.pi_ab, stage)

        self.method_record(self.p0_7, self.t0_7)

    def abmf(self):
        self.abmf = afterburner_mf(self.t0_5, self.t0_7, self.mf, self.fmf,
                                   self.nu_ab, self.cp_gas, self.LHV)

    def pi_nozzle_core(self):
        self.pi_nozzle_core = pi_nozzle(self.p, self.p_amb, 'Core')

    def nozzle_core(self, stage):
        print_color('Core flow', 'green')

        pi_nozzle_core = self.pi_nozzle_core if not isinstance(self.pi_nozzle_core, type(None)) else self.p / self.p_amb

        p_pc, self.choked = is_nozzle_choked(pi_nozzle_core, self.nu_nozzle_core, self.k_gas)

        if self.choked is True:
            self.p8, self.t8 = choked_nozzle(self.p, self.t, p_pc, self.k_gas, self.nu_nozzle_core,
                                             stage=stage)
        else:
            self.p8, self.t8 = non_choked_nozzle(self.p, self.t, self.p_amb, self.k_gas, self.nu_nozzle_core,
                                                 stage=stage)

        self.method_record(self.p8, self.t8)

    def exit_velocity(self):
        if self.choked is True:
            self.v8 = exit_velocity_choked(self.cp_gas, self.t0_7, self.t8, 'Core')
        else:
            self.v8 = exit_velocity_unchoked(self.k_gas, self.R, self.t8, 'Core')

        self.v0 = v0(self.k_air, self.R, self.T_amb, self.M)

    def nozzle_exit_area(self, stage):
        mf = self.mf+self.fmf if isinstance(self.abmf, type(None)) else self.mf+self.fmf+self.abmf
        self.A8 = A_exit(mf, self.t8, self.p8, self.v8, self.R, stage)

    def thrust_core(self):
        self.T_core = flow_thrust(self.mf+self.fmf, self.v8, self.v0, self.A8, self.p8, self.p0_0, self.choked)

    def sfc(self):
        tfmf = self.fmf + self.abmf if not isinstance(self.abmf, type(None)) else self.fmf
        self.sfc = sfc(tfmf, self.T_core)

    def method_record(self, p, t):
        self.p = p
        self.t = t
        self.record.append([self.p, self.t])

    def record_correction(self, i, p=None, t=None):
        if not isinstance(p, type(None)):
            self.record[i][0] = p
        if not isinstance(t, type(None)):
            self.record[i][1] = t
