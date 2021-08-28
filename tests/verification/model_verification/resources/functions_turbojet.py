from tests.verification.model_verification.resources.utils_propulsion import *


def afterburner(pbab, tbab, k, pi, nu, stage):
    """
    :param pbab: Total pressure ante afterburner
    :param tbab: Total temperature ante afterburner
    :param k: Specific heat capacity of gas flowing through afterburner
    :param pi: Afterburner pressure ratio
    :param nu: Afterburner isentropic efficiency
    :param stage: Stage
    :return:
    """
    p = pbab*pi
    t = tbab*(1-nu*(1-pi**((k-1)/k)))
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def afterburner_t_given(pbab, taab, pi, stage):
    """
    :param pbab: Total pressure ante afterburner
    :param taab: Total temperature post afterburner
    :param pi: Afterburner pressure ratio
    :param stage: Stage
    :return: Total pressure and temperature post combustion chamber
    """
    p = pbab * pi
    t = taab
    print_color('Afterburner', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def afterburner_mf(tbab, taab, mf, fmf, nu, cp, LHV):
    """
    :param tbab: Total temperature ante afterburner
    :param taab: Total temperature post afterburner
    :param mf: Gas mass flow
    :param fmf: Fuel mass flow
    :param nu: Afterburner isentropic efficiency
    :param cp: Specific heat capacity of flow through afterburner
    :param LHV: Fuel latent heat of vaporization
    :return:
    """
    abmf = (mf+fmf)*cp*(taab-tbab)/(nu*LHV)
    print_color('Afterburner fuel mass flow', 'yellow')
    print(units('SFC = {:,.4f}'.format(abmf), 'kg/s'))
    return abmf
