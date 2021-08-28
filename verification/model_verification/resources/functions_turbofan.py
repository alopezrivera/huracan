from alexandria.shell import print_color

from verification.model_verification.resources.utils_propulsion import *


def hot_mf(bpr, mf):
    print_color('Hot mass flow', 'green')
    print(units('Core ṁ = {:,.4f}'.format(mf/(bpr+1)), 'Kg/s'))
    return mf/(bpr+1)


def fan(pbf, tbf, k, pi, nu, stage=None):
    """
    Total pressure and temperature through turbofan fan
    :param pbf: Total pressure ante fan
    :param tbf: Total temperature ante fan
    :param k: Specific heat capacity of gas flowing through compressor
    :param pi: Compressor pressure ratio
    :param nu: Compressor isentropic efficiency
    :param stage: Stage
    :return: Total pressure and temperature after fan stage
    """
    p = pi*pbf
    t = tbf*(1+1/nu*(pi**((k-1)/k)-1))
    print_color('Fan', 'green')
    print(units('T0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', t), 'K')
          +
          units('\np0_{} = {:,.4f}'.format(stage if not isinstance(stage, type(None)) else 'n+1', p), 'Pa')
          )
    return p, t


def fan_power(tbf, taf, mf, cp):
    """
    Worked done on flow by fan
    :param tbf: Total temperature before fan
    :param taf: Total temperature after fan
    :param mf: ṁ through fan
    :param cp: Specific heat capacity of flow through fan
    :return: Work required by the flow on turbine
    """
    print_color('Fan power required', 'yellow')
    print(units('Ẇ_fan = {:,.4f}'.format(mf*cp*(taf-tbf)), 'W'))
    return mf*cp*(taf-tbf)
