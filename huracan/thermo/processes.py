# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0

"""
Huracan thermodynamic process functions
---------------------------------------
"""

from huracan.utils import setattr_namespace


class process:
    """
    Process data class
    """
    pass


def absolute(k,
             m, t_0, p_0):
    """
    Returns the absolute temperature and pressure of a gas
    flowing at a given
    - Mach number
    - Temperature
    - Pressure

    :param k:   [-]  Specific heat ratio
    :param m:   [M]  Flow Mach number
    :param t_0: [K]  Initial temperature
    :param p_0: [Pa] Initial pressure

    :type k:    (T: float) -> float
    :type m:    float
    :type t_0:  float
    :type p_0:  float

    :return:    process instance
    """

    p   = process()

    tau = (1+(k-1)/2*m**2)
    pi  = (1+(k-1)/2*m**2)**(k/(k-1))

    t0 = t_0*tau
    p0 = p_0*pi

    setattr_namespace(p, locals())

    return p


def diffusion(mf, cp, k, m, t_0, p_0,
              eta,
              t0=None, p0=None,
              PI=None, TAU=None):
    """
    Diffusion.

    Absolute temperature is considered constant through the process.

    The absolute pressure change is determined by the total pressure ratio
    _PI_ if provided. Else, _PI_ is calculated using the isentropic
    efficiency _nu_.

    :param mf:  [kg/s] Gas mass flow                    | -> Gas characteristics
    :param cp:  [-]    Constant pressure specific heat  |
    :param k:   [-]    Specific heat ratio              |
    :param m:   [M]    Flow Mach number                 |
    :param t_0: [K]    Initial temperature              |
    :param p_0: [Pa]   Initial pressure                _|
    :param eta: [-]    Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]    Pressure ratio                   |
    :param TAU: [-]    Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type m:    float
    :type t_0:  float
    :type p_0:  float
    :type eta:  float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    a = absolute(k, m, t_0, p_0)

    if isinstance(TAU, type(None)):
        TAU = 1
    if isinstance(PI, type(None)):
        pi  = (1+eta*(k-1)/2*m**2)**(k/(k-1))       # Pressure -> Total pressure
        PI  = pi/a.pi

    t00 = a.t0 if isinstance(t0, type(None)) else t0
    p00 = a.p0 if isinstance(p0, type(None)) else p0

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p


def compression(mf, cp, k, t00, p00,
                eta, PI=None, TAU=None,
                ):
    """
    Adiabatic compression.

    Input pairs:
        - eta, PI
            - TAU is calculated
        - eta, TAU
            - PI is calculated

    :param mf:  [kg/s] Gas mass flow                    | -> Gas characteristics
    :param cp:  [-]    Constant pressure specific heat  |
    :param k:   [-]    Specific heat ratio              |
    :param t00: [K]    Initial total temperature        |
    :param p00: [Pa]   Initial total pressure          _|
    :param eta: [-]    Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]    Pressure ratio                   |
    :param TAU: [-]    Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type t00:  float
    :type p00:  float
    :type eta:  float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
        "Compression process: neither PI nor TAU have been defined. At least one of them must be defined."

    if isinstance(TAU, type(None)):
        # calculate TAU
        TAU = 1+1/eta*(PI**((k-1)/k)-1)
    if isinstance(PI, type(None)):
        # calculate PI
        PI = (eta*(TAU-1)+1)**(k/(k-1))

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p


def expansion(mf, cp, k, t00, p00,
              eta, PI=None, TAU=None,
              ):
    """
    Adiabatic expansion.

    Input pairs:
        - PI, eta
            - TAU is calculated
        - TAU, eta
            - PI is calculated

    :param mf:  [kg/s] Gas mass flow                    | -> Gas characteristics
    :param cp:  [-]    Constant pressure specific heat  |
    :param k:   [-]    Specific heat ratio              |
    :param t00: [K]    Initial total temperature        |
    :param p00: [Pa]   Initial total pressure          _|
    :param eta: [-]    Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]    Pressure ratio                   |
    :param TAU: [-]    Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type t00:  float
    :type p00:  float
    :type eta:  float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
        "Expansion process: neither PI nor TAU have been defined. At least one of them must be defined."

    if isinstance(TAU, type(None)):
        # calculate TAU
        TAU = 1-eta*(1-PI**((k-1)/k))
    if isinstance(PI, type(None)):
        # calculate PI
        PI = (1-1/eta*(1-TAU))**(k/(k-1))

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p


def heat_exchange(mf, cp,
                  t00, p00,
                  Q_ex,
                  eta,
                  PI=1):
    """
    Constant pressure heat addition.
    - A pressure ratio PI may be specified if required.

    :param mf:       [kg/s] Gas mass flow
    :param cp:       [-]    Constant pressure specific heat
    :param t00:      [K]    Initial total temperature
    :param p00:      [Pa]   Initial total pressure
    :param Q_ex:     [K]    Heat received by the gas in the heat exchange
    :param eta:      [-]    Isentropic efficiency

    :type mf:        float
    :type fuel_mf:   float
    :type fuel_LHV:  float
    :type t00:       float
    :type p00:       float
    :type eta:       float
    """

    p = process()

    dt = eta*Q_ex/(mf*cp)

    t01 = t00 + dt
    p01 = p00*PI

    setattr_namespace(p, locals())

    return p


def combustion(mf, cp,
               t00, p00,
               fuel_mf, fuel_LHV,
               eta,
               PI=1):
    """
    Constant pressure heat addition.
    - A pressure ratio PI may be specified if required.

    :param mf:       [kg/s] Gas mass flow
    :param cp:       [-]    Constant pressure specific heat
    :param t00:      [K]    Initial total temperature
    :param p00:      [Pa]   Initial total pressure
    :param fuel_mf:  [kg/s] Fuel mass flow
    :param fuel_LHV: [J/kg] Fuel Lower Heating Value (heat of combustion)
    :param eta:      [-]    Isentropic efficiency

    :type mf:        float
    :type fuel_mf:   float
    :type fuel_LHV:  float
    :type t00:       float
    :type p00:       float
    :type eta:       float
    """

    Q_in = (fuel_mf*fuel_LHV)

    return heat_exchange(mf=mf, cp=cp,
                         t00=t00, p00=p00,
                         Q_ex=Q_in,
                         eta=eta,
                         PI=PI
                         )

