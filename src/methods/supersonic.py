def choking(pi_nozz, nu_nozz, k):
    """
    Choked flow is a phenomenon that occurs when a decrease in downstream
    pressure cannot cause a further increase in mass flow due to the
    reduced pressure at the choke point due to the Venturi effect.
    The pressure reduction causes a reduction in flow density and thus
    mass flow

    Determine whether the nozzle is choked:
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
    return p_pcrit, choked