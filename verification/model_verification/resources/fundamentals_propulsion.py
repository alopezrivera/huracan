from verification.model_verification.resources.functions_propulsion import *
from verification.model_verification.resources.utils_propulsion import *


def pi_compression(pi, nu, k, p, t):
    print_positive('Compression')
    p = pi*p
    t = t*(1+1/nu*(pi**((k-1)/k)-1))
    print_p_t(p, t)
    return p, t


def pi_expansion(pi, nu, k, p, t):
    print_positive('Expansion')
    p = pi*p
    t = t*(1-nu*(1-pi**((k-1)/k)))
    print_p_t(p, t)
    return p, t


def dt_expansion(pb, tb, dt, nu, k):
    print_positive('Expansion')
    t = tb - dt
    p = pb*(1-1/nu*(1-t/tb))**(k/(k-1))
    print_p_t(p, t)
    return p, t


def work_done(dt, mf, cp):
    print_positive('Work exerted')
    w_c = dt*mf*cp
    result('W_C', w_c, 'J')
    return w_c


def work_required(w_c, nu):
    print_positive('Work required')
    w_r = w_c/nu
    result('W_R', w_r, 'J')
    return w_r


def work_dt(w, mf, cp):
    print_positive('Work'+'\u0394'+'T')
    dt = w/mf/cp
    result('\u0394'+'T', dt, 'J')
    return dt


def nozzle(pbn, pamb, tbn, tan, tamb, nu_nozz, nu, mf, m, k=1.33, cp=1150, R=287, which='Core'):
    """
    :return: Nozzle results
    """

    "Choked nozzle"
    p_o_pcrit, choked = is_nozzle_choked(pbn/pamb, nu_nozz, k)

    if choked is True:
        "Pressure, temperature"
        print_positive('Nozzle'.format(which))
        p = pbn / p_o_pcrit
        pi = p / pbn
        t = tbn*(1-nu*(1-pi**((k-1)/k)))
        print_p_t(p, t)
        "Flow exit velocity"
        print_positive('{} exit velocity'.format(which))
        v = (2 * cp * (tbn - tan)) ** 0.5
        result('v{}'.format('8' if which == 'Core' else '18'), v, 'm/s')
    else:
        "Pressure, temperature"
        print_positive('Nozzle'.format(which))
        p = pamb
        pi = pamb / pbn
        t = tbn*(1-nu*(1-pi**((k-1)/k)))
        print_p_t(p, t)
        "Flow exit velocity"
        print_positive('{} exit velocity'.format(which))
        v = (k*R*tan)**0.5
        result('v{}'.format('8' if which == 'Core' else '18'), v, 'm/s')

    "Flow thrust"
    fn = mf*(v-v0(k, R, tamb, m))+A_exit(mf, t, p, v, R, 'n+1')*(p-pamb)
    result('T', fn, 'N')

    return p, t, v, fn
