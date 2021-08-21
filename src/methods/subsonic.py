def total_p(t_amb, m, k):
    """
    :param t_amb: Ambient temperature
    :param m: Mach number
    :param k: Specific heat capacity of gas flowing through inlet
    :return: Total pressure
    """
    t = t_amb*(1+(k-1)/2*m**2)
    return t


def total_t(p_amb, m, k):
    """
    TOTAL TEMPERATURE

    :param p_amb: Ambient pressure
    :param m: Mach number
    :param k: Specific heat capacity of gas flowing through inlet
    :return: Total temperature
    """
    p = p_amb*(1+(k-1)/2*m**2)**(k/(k-1))
    return p


def compression_pi(pi, nu, k, p, t):
    p = pi*p
    t = t*(1+1/nu*(pi**((k-1)/k)-1))
    return p, t


def expansion_pi(pi, nu, k, p, t):
    p = pi*p
    t = t*(1-nu*(1-pi**((k-1)/k)))
    return p, t


def expansion_dt(pb, tb, dt, nu, k):
    t = tb - dt
    p = pb*(1-1/nu*(1-t/tb))**(k/(k-1))
    return p, t


def combustion_t():
    pass


def combustion_p():
    pass
