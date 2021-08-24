from src.utils import setattr_namespace


class process:
    """
    Process data class
    """
    pass


def absolute(k,
             m, t_0, p_0):
    """
    Returns the absolute temperature and pressure of a gas
    flowing at a certain Mach number.

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
              nu, PI=None, TAU=None):
    """
    Diffusion process.

    Absolute temperature is considered constant through the process.

    Absolute pressure change is determined by the total pressure ratio
    _PI_ if provided. Else, _PI_ is calculated using the isentropic
    efficiency _nu_.

    :param mf:  [kg] Mass flow                        | -> Gas characteristics
    :param cp:  [-]  Constant pressure specific heat  |
    :param k:   [-]  Specific heat ratio              |
    :param m:   [M]  Flow Mach number                 |
    :param t_0: [K]  Initial temperature              |
    :param p_0:  [Pa] Initial pressure               _|
    :param nu:  [-]  Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]  Pressure ratio                   |
    :param TAU: [-]  Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type m:    float
    :type t_0:  float
    :type p_0:  float
    :type nu:   float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    a = absolute(k, m, t_0, p_0)

    if isinstance(TAU, type(None)):
        TAU = 1
    if isinstance(PI, type(None)):
        pi  = (1+nu*(k-1)/2*m**2)**(k/(k-1))       # Pressure -> Total pressure
        PI  = pi/a.pi

    t00 = a.t0
    p00 = a.p0

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p


def compression(mf, cp, k, t00, p00,
                nu, PI=None, TAU=None,
                ):
    """
    Compression process.

    Input pairs:
        - nu, PI
            - TAU is calculated
        - nu, TAU
            - PI is calculated

    :param mf:  [kg] Mass flow                        | -> Gas characteristics
    :param cp:  [-]  Constant pressure specific heat  |
    :param k:   [-]  Specific heat ratio              |
    :param t00: [K]  Initial total temperature        |
    :param p00: [Pa] Initial total pressure          _|
    :param nu:  [-]  Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]  Pressure ratio                   |
    :param TAU: [-]  Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type t00:  float
    :type p00:  float
    :type nu:   float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
        "Compression process: neither PI nor TAU have been defined. At least one of them must be defined."

    if isinstance(TAU, type(None)):
        # calculate TAU
        TAU = 1+1/nu*(PI**((k-1)/k)-1)
    if isinstance(PI, type(None)):
        # calculate PI
        PI = (nu*(TAU-1)+1)**(k/(k-1))

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p


def expansion(mf, cp, k, t00, p00,
              nu, PI=None, TAU=None,
              ):
    """
    Expansion process.

    Input pairs:
        - PI, nu
            - TAU is calculated
        - TAU, nu
            - PI is calculated

    :param mf:  [kg] Mass flow                        | -> Gas characteristics
    :param cp:  [-]  Constant pressure specific heat  |
    :param k:   [-]  Specific heat ratio              |
    :param t00: [K]  Initial total temperature        |
    :param p00: [Pa] Initial total pressure          _|
    :param nu:  [-]  Isentropic efficiency            | -> Process characteristics
    :param PI:  [-]  Pressure ratio                   |
    :param TAU: [-]  Temperature ratio               _|

    :type mf:   float
    :type cp:   float
    :type k:    float
    :type t00:  float
    :type p00:  float
    :type nu:   float
    :type PI:   float
    :type TAU:  float

    :return:    process instance
    """

    p   = process()

    assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
        "Expansion process: neither PI nor TAU have been defined. At least one of them must be defined."

    if isinstance(TAU, type(None)):
        # calculate TAU
        TAU = 1-nu*(1-PI**((k-1)/k))
    if isinstance(PI, type(None)):
        # calculate PI
        PI = (1-1/nu*(1-TAU))**(k/(k-1))

    t01 = t00*TAU
    p01 = p00*PI

    dt  = t00*(TAU-1)
    w   = cp*dt*mf

    setattr_namespace(p, locals())

    return p
