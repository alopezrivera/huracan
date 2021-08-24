from copy import deepcopy

from src.thermo.processes import absolute, diffusion, compression, expansion
from src.components import cycle, component


class fluid:
    """
    Fluid class
    """
    @classmethod
    def _diversion(cls, fluid, fraction):
        """
        Fluid diversion.

        :param fluid:    Fluid to be diverted.
        :param fraction: Fraction of diverted fluid.

        :type fluid:     mixture or fluid
        :type fraction:  float < 1

        :return:         [fluid] Core flow
                         [fluid] Diverted flow
        """
        div_f = deepcopy(fluid)

        div_f.mf *= fraction
        fluid.mf *= 1 - fraction

        return fluid, div_f

    def __init__(self, mf):
        """
        :param mf:  [kg] Mass flow

        :type mf:   float
        """
        self.mf = mf

    def __mul__(self, other):
        """
        Return two flows representing the diversion.
        """
        return self._diversion(self, other)

    def __rmul__(self, other):
        """
        Return two flows representing the diversion.
        """
        return self._diversion(self, other)


class gas(fluid):
    """
    Ideal gas class
    """
    def __init__(self, mf, cp, k,
                 m, t_0, p_0):
        """
        :param mf:  [kg] Mass flow
        :param cp:  [-]  Constant pressure specific heat
        :param k:   [-]  Specific heat ratio
        :param m:   [M]  Flow Mach number      |
        :param t_0: [K]  Initial temperature   | -> Total pressure and temperature calculated from inputs
        :param p_0: [Pa] Initial pressure      |

        :type cp:   (T: float) -> float
        :type k:    (T: float) -> float
        :type mf:   float
        :type m:    float
        :type t_0:  float
        :type p_0:  float
        """
        super().__init__(mf)
        self.cp = cp
        self.k = k

        self.m = m
        self.t_0 = t_0
        self.p_0 = p_0

        self.absolute()

    def __add__(self, other):
        """
        Mixture creation operator: <gas> + <gas>

        :type other: gas
        """
        return mixture(self, other)

    def __sub__(self, other):
        """
        Cycle creation operator: <gas> + <component/cycle>

        :type other: component or cycle

        :return:     cycle instance
        """
        if isinstance(other, component):
            c = cycle(self)-other
            return c
        elif isinstance(other, cycle):
            other.gas = self
            return other

    def absolute(self):
        """
        Returns the absolute temperature and pressure of a gas
        flowing at a certain Mach number.

        :return: process data class instance
        """

        k   = self.k(self.t_0)

        p = absolute(k   = k,
                     m   = self.m,
                     t_0 = self.t_0,
                     p_0 = self.p_0)

        self.t0 = p.t0
        self.p0 = p.p0

        return p

    def diffusion(self, nu,
                  PI=None,
                  TAU=None):
        """
        Diffusion
        ---------

        Assumptions:
        - Adiabatic
        - Reversible
        - Temperature remains constant through process

        The absolute pressure change is determined by the total pressure ratio
        _PI_ if provided. Else, _PI_ is calculated using the isentropic
        efficiency _nu_.

        :param nu:  [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio

        :type nu:   float
        :type PI:   float

        :return:    process instance
        """

        k   = self.k(self.t0)
        cp  = self.cp(self.t0)

        p = diffusion(mf  = self.mf,
                      cp  = cp,
                      k   = k,
                      m   = self.m,
                      t_0 = self.t_0,
                      p_0 = self.p_0,
                      nu  = nu,
                      PI  = PI,
                      TAU = TAU,
                      )

        self.t0 = p.t01
        self.p0 = p.p01

        return p

    def compression(self, nu,
                    PI=None,
                    TAU=None,
                    ):
        """
        Compression
        -----------

        Assumptions:
        - Adiabatic
        - Reversible

        Input pairs:
            - nu, PI
                - TAU is calculated
            - nu, TAU
                - PI is calculated

        :param nu:  [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type nu:   float
        :type PI:   float
        :type TAU:  float

        :return:    process instance
        """

        k   = self.k(self.t0)
        cp  = self.cp(self.t0)

        p   = compression(mf  = self.mf,
                          cp  = cp,
                          k   = k,
                          t00 = self.t0,
                          p00 = self.p0,
                          nu  = nu,
                          PI  = PI,
                          TAU = TAU,
                          )

        self.t0 = p.t01
        self.p0 = p.p01

        return p

    def expansion(self, nu,
                  PI=None,
                  TAU=None,
                  ):
        """
        Expansion
        ---------

        Assumptions:
        - Adiabatic
        - Reversible

        Input pairs:
            - PI, nu
                - TAU is calculated
            - TAU, nu
                - PI is calculated

        :param nu:  [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type nu:   float
        :type PI:   float
        :type TAU:  float

        :return:    process instance
        """

        k   = self.k(self.t0)
        cp  = self.cp(self.t0)

        p = expansion(mf  = self.mf,
                      cp  = cp,
                      k   = k,
                      t00 = self.t0,
                      p00 = self.p0,
                      nu  = nu,
                      PI  = PI,
                      TAU = TAU,
                      )

        self.t0 = p.t01
        self.p0 = p.p01

        return p


class mixture(gas):
    """
    Mixture class
    """

    @classmethod
    def _mix_t0(cls, gas1, gas2):
        """
        Total temperature of fluid mixture.
        """
        n = gas1.mf*gas1.cp(gas1.t0)*gas1.t0 + gas2.mf*gas2.cp(gas2.t0)*gas2.t0
        d = gas1.mf*gas1.cp(gas1.t0) + gas2.mf*gas2.cp(gas2.t0)
        t0_f = n / d
        return t0_f

    @classmethod
    def _mix_p0(cls, gas1, gas2):
        """
        Total pressure of fluid mixture.
        """
        n = gas1.p0*gas1.mf + gas2.p0*gas2.mf
        d = gas1.mf + gas2.mf
        p0_f = n / d
        return p0_f

    @classmethod
    def _mix_cp(cls, gas1, gas2):
        """
        Constant pressure specific heat at of fluid mixture.
        """
        cp_f = lambda t: (gas1.cp(t)*gas1.mf + gas2.cp(t)*gas2.mf) / (gas1.mf + gas2.mf)
        return cp_f

    @classmethod
    def _mix_k(cls, gas1, gas2):
        """
        Specific heat ratio of fluid mixture.
        """
        cp_f = lambda t: (gas1.k(t)*gas1.mf + gas2.k(t)*gas2.mf) / (gas1.mf + gas2.mf)
        return cp_f

    def __init__(self, gas1, gas2):
        """
        :param gas1: Mixture fluid 1
        :param gas2: Mixture fluid 2

        :type gas1:  gas or mixture
        :type gas2:  gas or mixture
        """

        mf = gas1.mf + gas2.mf
        super().__init__(mf  = mf,
                         cp  = self._mix_cp(gas1, gas2),
                         k   = self._mix_k(gas1, gas2),
                         m   = 0,
                         t_0 = self._mix_t0(gas1, gas2),
                         p_0 = self._mix_p0(gas1, gas2))


if __name__ == '__main__':

    mf = 700
    m  = 0.6
    t  = 288
    p  = 101325
    fr = 0

    g = gas(mf = mf,
            cp = lambda T: 1150 if T > 600 else 1000,
            k  = lambda T: 1.33 if T > 600 else 1.4,
            m  = m, t_0=t, p_0=p)

    f = gas(mf = mf,
            cp = lambda T: 1150 if T > 600 else 1000,
            k  = lambda T: 1.33 if T > 600 else 1.4,
            m  = m, t_0=t*fr, p_0=p*fr)

    k = gas(mf = mf,
            cp = lambda T: 1500 if T > 1000 else 1200 if T > 800 else 400,
            k  = lambda T: 1.33 if T > 600 else 1.4,
            m  = m, t_0=t*fr, p_0=p*fr)

    def t_mixture():
        global h
        h = g+f

        assert abs(h.t0 - g.t0/2) < 10e-12
        assert abs(h.p0 - g.p0/2) < 10e-12

    def t_diversion():
        mf = h.mf
        fr = 0.2
        i, j = fr*h

        assert i.mf == mf*(1-fr)
        assert j.mf == mf*fr

    t_mixture()
    t_diversion()
