from termcolor import colored


def units(s, u):
    if not isinstance(s, type(str)):
        s = str(s)
    return s + ' '*(35-len(s.replace("\n", ""))) + '[{}]'.format(u.rstrip())


def v0(k, r, t, m):
    """
    :param k: Specific heat capacity of free stream air
    :param r: Gas constant = 287J/Kg/K
    :param t: Ambient temperature
    :param m: Free stream Mach number
    :return:
    """
    return m*(k*r*t)**0.5


def turbine_dt(w, mf, cp):
    """
    Change of temperature due to work done by flow to power turbine in turbine stage
    :param w: Work done by flow on turbine
    :param mf: Mass flow through turbine
    :param cp: Specific heat capacity of flow through turbine
    :return: Turbine ∆T
    """
    return print(units('∆T = {:,.4f}'.format(-w/(mf*cp)), '°C'))


def is_nozzle_choked(nu_nozz, k):
    """
    Determining whether the nozzle is choked:
        Choked:
            total pressure after nozzle will equal pcrit = (p/p_crit)^-1 * p
        Non-choked:
            total pressure after nozzle will equal p
    :param nu_nozz: Nozzle isentropic efficiency
    :param k: Specific heat capacity of gas flowing through nozzle
    :return: Nozzle condition
    """
    p_pcrit = 1/(1-1/nu_nozz*((k-1)/(k+1)))**(k/(k-1))
    print(colored('{} nozzle '.format('Choked' if p_pcrit > 1 else 'Non choked'),
                  'green' if p_pcrit < 1 else 'red') + '\n    p/p_crit = {}'.format(p_pcrit))
    return p_pcrit


def print_color(text, color):
    print(colored(text, color))

