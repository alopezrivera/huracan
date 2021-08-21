import copy

from src.utils import setattr_namespace


class process:
    """
    Process data class
    """
    pass


class fluid:
    """
    Fluid class
    """
    @classmethod
    def diversion(cls, fluid, fraction):
        """
        Fluid diversion.

        :param fluid:    Fluid to be diverted.
        :param fraction: Fraction of diverted fluid.

        :type fluid:     mixture or fluid
        :type fraction:  float < 1

        :return:         [fluid] Core flow
                         [fluid] Diverted flow
        """
        div_f = copy.deepcopy(fluid)

        div_f.mf *= fraction
        fluid.mf *= 1 - fraction

        return fluid, div_f

    def __init__(self, mf,
                 m=None, t0=None, p0=None,
                 t00=None, p00=None):
        """
        :param mf:  [kg] Mass flow

        :type mf:   float
        """
        self.mf = mf

    def __add__(self, other):
        """
        Create mixture.
        """
        return mixture(self, other)

    def __mul__(self, other):
        """
        Return two flows representing the diversion.
        """
        return self.diversion(self, other)

    def __rmul__(self, other):
        """
        Return two flows representing the diversion.
        """
        return self.diversion(self, other)


class mixture(fluid):
    """
    Mixture class
    """

    @classmethod
    def mix_t(cls, fluid1, fluid2):
        n = fluid1.mf*fluid1.cp*fluid1.t00 + fluid2.mf*fluid2.cp*fluid2.t00
        d = fluid1.mf*fluid1.cp + fluid2.mf*fluid2.cp
        t00_f = n/d
        return t00_f

    @classmethod
    def mix_p(cls, fluid1, fluid2):
        n = fluid1.p00*fluid1.mf + fluid2.p00*fluid2.mf
        d = fluid1.mf + fluid2.mf
        p00_f = n/d
        return p00_f

    def __init__(self, fluid1, fluid2):
        """
        :param fluid1: Mixture fluid 1
        :param fluid2: Mixture fluid 2

        :type fluid1:  fluid, mixture
        :type fluid2:  fluid, mixture
        """
        if isinstance(fluid1, mixture):
            pass
        if isinstance(fluid2, mixture):
            pass

        mf = fluid1.mf + fluid2.mf
        super().__init__(mf)

        self.p00 = self.mix_p(fluid1, fluid2)
        self.t00 = self.mix_t(fluid1, fluid2)


class fuel(fluid):
    """
    Fuel class
    """
    def __init__(self, mf, LHV):
        """
        :param mf:
        :param LHV:
        """
        super().__init__(mf)
        self.LHV = LHV


class gas(fluid):
    """
    Gas class
    """
    def __init__(self, mf, cp, k):
        """
        :param mf:  [kg] Mass flow
        :param cp:  [-]  Specific heat capacity
        :param k:   [-]  Specific heat capacity

        :type cp:   (T: float) -> float
        :type k:    (T: float) -> float
        :type mf:   float
        """
        super().__init__(mf)
        self.cp = cp
        self.k = k

    def absolute(self, m,
                 t0, p0):
        """
        Returns the absolute temperature and pressure of a gas
        flowing at a certain Mach number.

        :param m:   [M]  Flow Mach number
        :param t0:  [K]  Initial temperature
        :param p0:  [Pa] Initial pressure

        :type m:    float
        :type t0:   float
        :type p0:   float

        :return:    dict: t00 [float] Total temperature
                          p00 [float] Total pressure
        """

        p   = process()

        k   = self.k(t0)

        PI  = (1+(k-1)/2*m**2)**(k/(k-1))
        TAU = (1+(k-1)/2*m**2)

        t00 = t0*TAU
        p00 = p0*PI

        setattr_namespace(p, locals())

        return p

    def diffusion(self, nu, m,
                  t00, p00,
                  PI=None,
                  TAU=None):
        """
        Diffusion process.

        Absolute temperature is considered constant through the process.

        Absolute pressure change is determined by the total pressure ratio
        _PI_ if provided. Else, _PI_ is calculated using the isentropic
        efficiency _nu_.

        :param nu:  [-]  Isentropic efficiency
        :param m:   [M]  Flow Mach number
        :param t00: [K]  Initial total temperature
        :param p00: [Pa] Initial total pressure
        :param PI:  [-]  Pressure ratio

        :type nu:   float
        :type m:    float
        :type t00:  float
        :type p00:  float
        :type PI:   float

        :return:    dict: t01 [float] Total temperature after diffusion process
                          p01 [float] Total pressure after diffusion process
        """

        p   = process()

        k   = self.k(t00)
        cp  = self.cp(t00)

        if isinstance(PI, type(None)):
            pi = (1+nu*(k-1)/2*m**2)**(k/(k-1))             # Temperature -> Total temperature
            PI = pi/self.absolute(m, 0, 0).PI               # Temperature and pressure placeholders

        if isinstance(TAU, type(None)):
            TAU = 0

        dt  = t00*(TAU-1)

        t01 = t00
        p01 = p00*PI
        w   = cp*dt*self.mf

        setattr_namespace(p, locals())

        return p

    def compression(self, nu,
                    t00, p00,
                    PI=None,
                    TAU=None,
                    ):
        """
        Compression process.

        Input pairs:
            - nu, PI
                - TAU is calculated
            - nu, TAU
                - PI is calculated

        :param nu:  [-]  Isentropic efficiency
        :param t00: [K]  Initial total temperature
        :param p00: [Pa] Initial total pressure
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type nu:   float
        :type t00:  float
        :type p00:  float
        :type PI:   float
        :type TAU:  float

        :return:    dict: t01 [float] Total temperature after compression process
                          p01 [float] Total pressure after compression process
        """

        p   = process()

        k   = self.k(t00)
        cp  = self.cp(t00)

        assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
            "Compression process: neither PI nor TAU have been defined. At least one of them must be defined."

        if isinstance(PI, type(None)):
            # calculate PI
            PI = (nu*(TAU-1)+1)**(k/(k-1))
        if isinstance(TAU, type(None)):
            # calculate TAU
            TAU = 1+1/nu*(PI**((k-1)/k)-1)

        dt  = t00*(TAU-1)

        t01 = t00*TAU
        p01 = p00*PI
        w   = cp*dt*self.mf

        setattr_namespace(p, locals())

        return p

    def expansion(self, nu,
                  t00, p00,
                  PI=None,
                  TAU=None,
                  ):
        """
        Expansion process.

        Input pairs:
            - PI, nu
                - TAU is calculated
            - TAU, nu
                - PI is calculated

        :param nu:  [-]  Isentropic efficiency
        :param t00: [K]  Initial total temperature
        :param p00: [Pa] Initial total pressure
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type nu:   float
        :type t00:  float
        :type p00:  float
        :type PI:   float
        :type TAU:  float

        :return:    dict: t01 [float] Total temperature after expansion process
                          p01 [float] Total pressure after expansion process
        """

        p   = process()

        k   = self.k(t00)
        cp  = self.cp(t00)

        assert not isinstance(PI, type(None)) or not isinstance(TAU, type(None)), \
            "Expansion process: neither PI nor TAU have been defined. At least one of them must be defined."

        if isinstance(PI, type(None)):
            # calculate PI
            PI = (1-1/nu*(1-TAU))**(k/(k-1))
        if isinstance(TAU, type(None)):
            # calculate TAU
            TAU = 1-nu*(1-PI**((k-1)/k))

        dt  = t00*(TAU-1)

        t01 = t00*TAU
        p01 = p00*PI
        w   = cp*dt*self.mf

        setattr_namespace(p, locals())

        return p


if __name__ == '__main__':

    def test_gas():
        g = gas(1450,
                lambda T: 1150 if T > 600 else 1000,
                lambda T: 1.33 if T > 600 else 1.4)
        a = g.absolute(0.6, 288, 101325)
        b = g.diffusion(0.9, 0.8, 300, 121325)
        c = g.compression(0.85, 450, 200000, PI=14)
        d = g.expansion(0.85, 893.9732886318843, 2800000, TAU=0.3)

    def test_fuel():
        f = fuel(10, 43e6)

    def test_mixture():
        pass

    def test_diversion():
        mf = 1450
        fr = 0.2

        g = gas(mf,
                lambda T: 1150 if T > 600 else 1000,
                lambda T: 1.33 if T > 600 else 1.4)

        g, gg = g * fr

        assert g.mf == mf * (1 - fr)
        assert gg.mf == mf * fr

