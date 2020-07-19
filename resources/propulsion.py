from utils import *


def ambient(pamb, tamb, m, k):
    """
    :param pamb: Ambient pressure
    :param tamb: Ambient temperature
    :param m: Mach number
    :param k: Specific heat capacity of gas flowing through inlet
    :return: Total ambient pressure and temperature
    """
    print_color('Ambient', 'green')
    p = pamb * (1 + (k - 1) / 2 * m ** 2) ** (k / (k - 1))
    t = tamb * (1 + (k - 1) / 2 * m ** 2)
    print(units('t0_0 = {:,.4f}'.format(t), 'K')
          +
          units('\np0_0 = {:,.4f}'.format(p), 'Pa')
          )
    return p, t


def inlet(p_amb_abs, t_amb_abs, k, pi, nu):
    """
    Total pressure and temperature through inlet
    :param p_amb_abs: Total ambient pressure
    :param t_amb_abs: Total ambient temperature
    :param k: Specific heat capacity of gas flowing through compressor
    :param pi: Inlet pressure ratio
    :return: Total pressure and temperature post inlet
    """
    print_color('Inlet', 'green')
    p = p_amb_abs*pi
    t = t_amb_abs*(1+1/nu*(pi**((k-1)/k)-1))
    print(units('T0_2 = {:,.4f}'.format(t), 'K')
          +
          units('\np0_2 = {:,.4f}'.format(p), 'Pa')
          )
    return p, t


def compressor(pbc, tbc, k, pi, nu, stage=None, kind=None):
    """
    Total pressure and temperature through compressor stage
    :param pbc: Total pressure ante compressor
    :param tbc: Total temperature ante compressor
    :param k: Specific heat capacity of gas flowing through compressor
    :param pi: Compressor pressure ratio
    :param nu: Compressor isentropic efficiency
    :param stage: Stage
    :param kind: HPC, LPC
    :return: Total pressure and temperature post compressor stage
    """
    p = pi*pbc
    t = tbc*(1+1/nu*(pi**((k-1)/k)-1))
    print_color('{}'.format(kind), 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def compr_work(mf, cp, Tbc, Tac, which='LPC'):
    """
    Work done by compressor
    :param mf: ṁ through compressor
    :param cp: Specific heat capacity of gas through compressor
    :param Tbc: T ante compressor stage
    :param Tac: T post compressor stage
    :param which: LPC or HPC
    :return: Worked done by compressor
    """
    w_comp = mf*cp*(Tac-Tbc)
    print_color('Compressor work on flow', 'green')
    print(units('Ẇ_{} = {:,.4f}'.format(which, w_comp), 'W'))
    return w_comp


def fuel_mass_flow(tbc, tac, mf, cp, nu, lhv):
    """
    Fuel mass flow
    :param tbc: Temperature ante combustion
    :param tac: Temperature post combustion
    :param mf: ṁ through combustion chamber/afterburner
    :param cp: Specific heat capacity of hot gas through compressor
    :param nu: Combustion chamber/afterburner isentropic efficiency
    :param lhv: Fuel latent heat of vaporization
    :return: Fuel ṁ
    """
    dt = tac-tbc
    fmf = mf*cp*dt/(lhv*nu)
    print_color('Fuel mass flow', 'green')
    print(units('Fuel ṁ = {:,.4f}'.format(fmf), 'Kg/s'))
    return


def turbine(w, mf, cp, k, nu, tbt, pbt, stage=None, kind=None):
    """
    Total pressure and temperature through turbine stage
    :param w: Work done by flow on turbine
    :param mf: ṁ through turbine
    :param cp: Specific heat capacity of flow through turbine
    :param k: Specific heat capacity of gas flowing through compressor
    :param nu: Turbine isentropic efficiency
    :param tbt: Total temperature ante turbine
    :param pbt: Total pressure ante turbine
    :param stage: Stage
    :param kind:
    :return: Total pressure and temperature post turbine stage
    """
    t = tbt - w/(mf*cp)
    p = pbt*(1-1/nu*(1-t/tbt))**(k/(k-1))
    print_color('{}'.format(kind), 'blue')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def turbine_pr(mf, cp, Tbc, Tac, nu_spool, which='LPT'):
    """
    Turbine power required
    :param mf: ṁ through compressor
    :param cp: Specific heat capacity of gas through compressor
    :param Tbc: T ante compressor stage
    :param Tac: T post compressor stage
    :param nu_spool: Spool mechanical efficiency
    :param which: LPC or HPC
    :return: Power required from turbine
    """
    w_comp = mf*cp*(Tac-Tbc)
    p_turb = w_comp/nu_spool
    print_color('Turbine power required', 'green')
    print(units('Ẇ_{} = {:,.4f}'.format(which, p_turb), 'W'))
    return p_turb


def cc_pressure(pbcc, tacc, pi, stage):
    p = pbcc*pi
    print_color('Combustion chamber pressure', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', tacc), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, tacc


def non_choked_nozzle(pbn, tbn, pamb, k, nu, stage=None):
    """
    Total pressure and temperature through non-choked nozzle
    :param pbn: Total pressure ante nozzle
    :param tbn: Total temperature ante nozzle
    :param pamb: Ambient pressure
    :param k: Specific heat capacity of gas flowing through nozzle
    :param nu: Nozzle isentropic efficiency
    :param stage: Stage
    :return: Total pressure and temperature post non-choked nozzle stage
    """
    pi = pamb/pbn
    t = tbn*(1-nu*(1-pi**((k-1)/k)))
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', pamb), 'Pa')
          )
    return pamb, t


def choked_nozzle(pbn, tbn, p_pc, k, nu, stage=None):
    """
    Total pressure and temperature through choked nozzle
    :param pbn: Total pressure ante nozzle
    :param tbn: Total temperature ante nozzle
    :param p_pc: Total pressure post combustion chamber
    :param k: Specific heat capacity of gas flowing through nozzle
    :param nu: Nozzle isentropic efficiency
    :param stage: Stage
    :return: Total pressure and temperature post choked nozzle stage
    """
    p = pbn/p_pc
    pi = p/pbn
    t = tbn*(1-nu*(1-pi**((k-1)/k)))
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def exit_velocity(k, r, t, which):
    """
    Core -non bypass- flow velocity
    :param k: Specific heat capacity of gas exiting nozzle
    :param r: Ideal gas constant (287)
    :param t: Total temperature post nozzle
    :param which: Core or bypass
    :return: Flow velocity at nozzle exit -core flow velocity-
    """
    print_color('{} exit velocity'.format(which), 'green')
    print(units('v = {:,.4f}'.format((k*r*t)**0.5), 'm/s'))
    return (k*r*t)**0.5


def flow_thrust(mf, van, v0, which='Core'):
    """
    Thrust generated by jet
    :param mf: ṁ through
    :param van: Flow velocity at nozzle exit
    :param v0: Free stream velocity
    :param which: Core or bypass
    :return: Thrust generated by jet
    """
    print_color('Flow thrust', 'green')
    print(units('T_{} = {:,.4f}'.format(which, 2*mf*(van-v0)), 'N'))
    return 2*mf*(van-v0)

