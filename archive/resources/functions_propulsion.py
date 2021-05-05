from resources.utils_propulsion import *


def ambient(pamb, tamb, m, k):
    """
    :param pamb: Ambient pressure
    :param tamb: Ambient temperature
    :param m: Mach number
    :param k: Specific heat capacity of gas flowing through inlet
    :return: Total ambient pressure and temperature
    """
    print_color('Ambient', 'green')
    p = pamb*(1+(k-1)/2*m**2)**(k/(k-1))
    t = tamb*(1+(k-1)/2*m**2)
    print(units('t0_0 = {:,.4f}'.format(t), 'K')
          +
          units('\np0_0 = {:,.4f}'.format(p), 'Pa')
          )
    return p, t


def inlet(pamb, tamb, m, k, pi, nu):
    """
    :param pamb: Ambient pressure
    :param tamb: Ambient temperature
    :param m: Mach number
    :param k: Specific heat capacity of gas flowing through inlet
    :param pi: Inlet pressure ratio
    :param nu: Inlet isentropic efficiency
    :return: Total pressure and temperature after inlet
    """
    p = pi*pamb*(1+(k-1)/2*m**2)**(k/(k-1))
    t = tamb*(1+(k-1)/2*m**2)
    p_nu = pi*pamb*(1+nu*(k-1)/2*m**2)**(k/(k-1))
    print_color('Inlet', 'green')
    if nu != 1:
        print(units('t0_2 = {:,.4f}'.format(t), 'K')
              +
              units('\np0_2 = {:,.4f} [nu = 1]'.format(p), 'Pa')
              +
              units('\np0_2 = {:,.4f} [nu = {}]'.format(p_nu, nu), 'Pa'))
    else:
        print(units('t0_2 = {:,.4f}'.format(t), 'K')
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
    print_color('{}'.format(kind), 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def compr_work(mf, cp, tbc, tac, which='LPC'):
    """
    Work done by compressor
    :param mf: ṁ through compressor
    :param cp: Specific heat capacity of gas through compressor
    :param tbc: T ante compressor stage
    :param tac: T post compressor stage
    :param which: LPC or HPC
    :return: Worked done by compressor
    """
    w_comp = mf*cp*(tac-tbc)
    print_color('{} work on flow'.format(which), 'yellow')
    print(units('Ẇ_{} = {:,.4f}'.format(which.lower(), w_comp), 'W'))
    return w_comp


def turbine_pr(w_comp, nu, which='LPT'):
    """
    Turbine power required
    :param w_comp: work exerted by compressor in shared spool
    :param nu_spool: Spool mechanical efficiency
    :param which: LPC or HPC
    :return: Power required from turbine
    """
    p_turb = w_comp/nu
    print_color('{} power required'.format(which), 'yellow')
    print(units('Ẇ_{} = {:,.4f}'.format(which, p_turb), 'W'))
    return p_turb


def turbine_dt(w, mf, cp):
    """
    Change of temperature due to work done by flow to power turbine in turbine stage
    :param w: Work done by flow on turbine
    :param mf: Mass flow through turbine
    :param cp: Specific heat capacity of flow through turbine
    :return: Turbine ∆T
    """
    return print(units('∆T = {:,.4f}'.format(-w/(mf*cp)), '°C'))


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
    print_color('Fuel mass flow', 'yellow')
    print(units('Fuel ṁ = {:,.4f}'.format(fmf), 'Kg/s'))
    return fmf


def cc_t_given(pbcc, tacc, pi, stage):
    """
    :param pbcc: Total pressure ante combustion chamber
    :param tacc: Total temperature post combustion chamber
    :param pi: Combustion chamber pressure ratio
    :param stage: Stage
    :return: Total pressure and temperature post combustion chamber
    """
    p = pbcc*pi
    print_color('Combustion chamber', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', tacc), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, tacc


def cc_dt_given(pbcc, tbcc, dt, pi, stage):
    """
    :param pbcc: Total pressure ante combustion chamber
    :param tbcc: Total temperature after combustion chamber
    :param dt: Total temperature gradient after combustion chamber
    :param pi: Combustion chamber pressure ratio
    :param stage: Stage
    :return: Total pressure and temperature post combustion chamber
    """
    p = pbcc*pi
    t = tbcc + dt
    print_color('Combustion chamber', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def cc_fmf_given(pbcc, tbcc, pi, mf, fmf, nu, cp, LHV, stage):
    """
    :param pbcc: Total pressure ante combustion chamber
    :param tbcc: Total temperature after combustion chamber
    :param pi: Combustion chamber pressure ratio
    :param mf: Air mass flow
    :param fmf: Fuel mass flow
    :param nu: Combustion chamber isentropic efficiency
    :param cp: Specific heat capacity of hot gas through combustion chamber
    :param LHV: Fuel latent heat of vaporization
    :param stage: Stage
    :return: Total pressure and temperature post combustion chamber
    """
    p = pbcc*pi
    t = tbcc + nu*fmf*LHV/(mf*cp)
    print_color('Combustion chamber', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', tbcc), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def cc_t_interturbine(pbcc, t_inter, pi, w_comp, mf, cp, nu, stage):
    """
    :param pbcc: Total pressure before combustion chamber
    :param t_inter: Total interturbine temperature
    :param pi: Combustion chamber pressure ratio
    :param w_comp: HPC work on flow
    :param mf: Mass flow through combustion chamber
    :param cp: Specific heat capacity of hot gas through combustion chamber
    :param nu: Combustion chamber isentropic efficiency
    :param stage: Stage
    :return: Total pressure and temperature at combustion chamber exit
    """
    p = pbcc*pi
    t = t_inter + w_comp/mf/cp/nu
    print_color('Combustion chamber', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def cc_w_given(pbcc, tbcc, pi, w_HPT, w_LPT, mf, cp, nu, stage):
    """
    :param pbcc: Total pressure before combustion chamber
    :param tbcc: Total temperature after combustion chamber
    :param pi: Combustion chamber pressure ratio
    :param w_HPT: HPT work required
    :param w_LPT: LPT work required
    :param mf: Mass flow through combustion chamber
    :param cp: Specific heat capacity of hot gas through combustion chamber
    :param nu: Combustion chamber isentropic efficiency
    :param stage: Stage
    :return: Total pressure and temperature at combustion chamber exit
    """
    p = pbcc*pi
    t = tbcc + (w_HPT+w_LPT)/mf/cp
    t_nu = tbcc + (w_HPT+w_LPT)/mf/cp/nu
    print_color('Combustion chamber', 'green')
    if nu != 1:
        print(units('T0_{} = {:,.4f} [nu = 1]'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
              +
              units('\nT0_{} = {:,.4f} [nu = {}]'.format(stage if not isinstance(stage, type(None)) else 'n+1', t_nu, nu), 'K')
              +
              units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
              )
    else:
        print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
              +
              units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
              )
    return p, t


def pi_nozzle(p_nozzle, p_amb, which):
    """
    :param p_nozzle: Pressure before nozzle exit
    :param p_amb: Ambient pressure
    :param which: Which
    :return: Nozzle pressure ratio
    """
    pi = p_nozzle/p_amb
    print_color('{} pressure ratio'.format(which), 'yellow')
    print(units('pi_{} = {:,.4f}'.format(which.lower(), pi), '-'))
    return pi


def is_nozzle_choked(pi_nozz, nu_nozz, k):
    """
    Determining whether the nozzle is choked:
        Choked:
            total pressure after nozzle will equal pcrit = (p/p_crit)^-1 * p
        Non-choked:
            total pressure after nozzle will equal p
    :param pi_nozz: Nozzle expansion ratio
    :param nu_nozz: Nozzle isentropic efficiency
    :param k: Specific heat capacity of gas flowing through nozzle
    :return: Nozzle condition
    """
    p_pcrit = 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))
    choked = pi_nozz > p_pcrit
    print(colored('{} nozzle '.format('Choked' if choked is True else 'Non choked'),
                  'red' if pi_nozz > p_pcrit else 'green') + '\n    p/p_crit = {}'.format(p_pcrit))
    return p_pcrit, choked


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
    print(units('T{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', pamb), 'Pa')
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
    print(units('T{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def exit_velocity_choked(cp, tbn, tan, which):
    """
    Choked exit flow velocity
    :param cp: Specific heat capacity of hot gas through nozzle
    :param tbn: Total temperature before nozzle
    :param tan: Total temperature after nozzle
    :param which: Core or bypass
    :return: Flow velocity at nozzle exit -core flow velocity-
    """
    v = (2*cp*(tbn-tan))**0.5
    den = '8' if which == 'Core' else '18'
    print_color('{} exit velocity'.format(which), 'yellow')
    print(units('v{} = {:,.4f}'.format(den, v), 'm/s'))
    return v


def exit_velocity_unchoked(k, R, tan, which):
    """
    Unchoked exit flow velocity
    :param k: Specific heat capacity of gas flowing through nozzle
    :param R: Ideal gas constant (287)
    :param tan: Total temperature after nozzle
    :param which: Core or bypass
    :return: Flow velocity at nozzle exit -core flow velocity-
    """
    v = (k*R*tan)**0.5
    den = '8' if which == 'Core' else '18'
    print_color('{} exit velocity'.format(which), 'yellow')
    print(units('v{} = {:,.4f}'.format(den, v), 'm/s'))
    return v


def A_exit(mf, t_exit, p_exit, v_exit, R, stage):
    """
    :param mf: Mass flow through nozzle
    :param t_exit: Temperature at exit of fan nozzle
    :param p_exit: Pressure at fan nozzle exit
    :param v_exit: Flow velocity at exit of fan nozzle
    :param R: Ideal gas constant (287)
    :param stage: Stage
    :return: Fan nozzle equivalent area
    """
    A_exit = mf * R * t_exit / (p_exit * v_exit)
    print_color('A{}'.format(stage), 'yellow')
    print(units('A{} = {:,.4f}'.format(stage, A_exit), 'm^2'))
    return A_exit


def flow_thrust(mf, van, v0, A_exit, pan, p0, choked, which='Core'):
    """
    Thrust generated by jet
    :param mf: ṁ through
    :param van: Flow velocity at nozzle exit
    :param v0: Free stream velocity
    :param A_exit: Nozzle exit area
    :param pan: Pressure at nozzle exit
    :param p0: Total pressure at inlet
    :param choked: Whether nozzle is choked or not
    :param which: Core or bypass
    :return: Thrust generated by jet
    """
    if choked is True:
        fn = mf*(van - v0) + A_exit*(pan - p0)
    else:
        fn = mf*(van - v0)
    print_color('{} thrust'.format(which), 'yellow')
    print(units('T_{} = {:,.4f}'.format(which, fn), 'N'))
    return fn


def sfc(tfmf, T_core):
    """
    :param tfmf: Total fuel mass flow
    :param T_core: Core flow thrust
    :return: Specific fuel consumption
    """
    sfc = tfmf/(T_core)
    print_color('Specific fuel consumption', 'yellow')
    print(units('SFC = {:,.4f}E-5'.format(sfc*10e4), 'kg/s/N'))
    return sfc


def intercooler_t_given(pbic, taic, pi, stage):
    """
    :param pbic: Total pressure before intercooler
    :param taic: Total temperature after intercooler
    :param pi: Intercooler pressure ratio
    :return: Total temperature and pressure after intercooler
    :param stage: Stage
    """
    p, t = pbic*pi, taic
    print_color('Intercooler', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def intercooler_f(E_intercooler, hmf, cmf,
                  tbic_core, taic_core,
                  tbic_bp, taic_bp):
    """
    :param E_intercooler: Intercooler efficiency
    :param hmf: Hot (core) mass flow
    :param cmf: Cold (bypass) mass flow
    :param tbic_core: Core flow total temperature before intercooler
    :param taic_core: Core flow total temperature after intercooler
    :param tbic_bp: Bypass flow total temperature before intercooler
    :param taic_bp: Bypass flow total temperature after intercooler
    :param cp: Specific heat capacity of hot gas through recuperator
    :return: Bypass air fraction needed
    """
    f = hmf*(tbic_core-taic_core)/cmf/(taic_bp-tbic_bp)/E_intercooler
    print_color('Intercooler bypass flow fraction', 'yellow')
    print(units('f = {:,.4f}'.format(f), '-'))
    return f


def recuperator_heat(E_recuperator, tbr_core, dt, cp_air, cp_gas,
                     pbr_core, pi_rec_comp, stage):
    """
    :param E_recuperator: Recuperator efficiency
    :param tbr_core: Core flow total temperature before recuperator heat addition
    :param dt: Total temperature gradient due to recuperator stage -before nozzle-
    :param cp_air: Specific heat capacity of bypass (cold) gas through recuperator
    :param cp_gas: Specific heat capacity of core (hot) gas through recuperator
    :param stage: Stage
    :return: Total core temperature before combustion chamber
    """
    tar_cc = tbr_core + E_recuperator*cp_gas*dt/cp_air
    par_cc = pbr_core*pi_rec_comp
    print_color('Recuperator heat addition', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', tar_cc), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', par_cc), 'Pa')
          )
    return par_cc, tar_cc


def recuperator_remove(tbr_nozzle, dt, pbr_nozzle, pi_rec_nozzle, stage):
    """
    :param tbr_nozzle: Core total temperature before recuperator heat removal
    :param dt: Recuperator temperature gradient
    :param stage: Stage
    :return: Core total temperature after recuperator heat removal
    """
    tar_nozzle = tbr_nozzle - dt
    par_nozzle = pbr_nozzle*pi_rec_nozzle
    print_color('Recuperator heat removal', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', tar_nozzle), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', par_nozzle), 'Pa')
          )
    return par_nozzle, tar_nozzle


def hp(p):
    return p*0.735499*1000


def fuel_to_air_real(fa_real, fa_stoich):
    if fa_real > fa_stoich:
        print_color('Rich combustion', 'red')
    else:
        print_color('Lean combustion', 'red')


def compression_pi(pbc, tbc, k, pi, nu):
    p = pi*pbc
    t = tbc*(1+1/nu*(pi**((k-1)/k)-1))
    return p, t


def compression_tr(pbc, tbc, k, tr, nu):
    t = tbc*tr
    p = pbc*(1+nu*(t/tbc-1))**(k/(k-1))
    return p, t


def expansion_pi(pbe, tbe, k, pi, nu):
    p = pbe*pi
    t = tbe*(1-nu*(1-pi**((k-1)/k)))
    return p, t


def expansion_tr(pbe, tbe, k, tr, nu):
    t = tbe*tr
    p = pbe*(1+nu*(t/tbe-1))**(k/(k-1))
    return p, t


def mach(v0, k, r, t):
    return v0/(k*r*t)**0.5


def v0(k, r, t, m):
    """
    :param k: Specific heat capacity of free stream air
    :param r: Gas constant = 287J/Kg/K
    :param t: Ambient temperature
    :param m: Free stream Mach number
    :return: Free stream flow velocity
    """
    return m*(k*r*t)**0.5