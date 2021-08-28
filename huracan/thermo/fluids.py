from copy import deepcopy

from huracan.thermo.processes import absolute, diffusion, compression, combustion, expansion
from huracan.engine import stream, component


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

        :type mf:   float
        :type cp:   (T: float) -> float
        :type k:    (T: float) -> float
        :type m:    float
        :type t_0:  float
        :type p_0:  float
        """
        self.mf = mf
        self.cp = cp
        self.k = k

        self.m = m
        self.t_0 = t_0
        self.p_0 = p_0

        self.absolute()

    def __add__(self, other):
        """
        Mixture creation operator: <gas> + <gas>

        In the case of adding fuel to a gas, the
        following assumptions are considered:
        - Total temperature and pressure of gas are
          unaltered.
        - Constant pressure specific heat capacity Cp
          of gas is unaltered.
        - Ratio of specific heats k of gas is unaltered.

        :type other: gas or fuel
        """
        if isinstance(other, gas):
            return mixture(self, other)
        if isinstance(other, fuel):
            self.mf += other.mf
            return self

    def __sub__(self, other):
        """
        Stream creation operator: <gas> + <component/stream>

        :type other: component or stream

        :return:     stream instance
        """
        if isinstance(other, component):
            s = stream(self)-other
            return s
        elif isinstance(other, stream):
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

    def diffusion(self, eta,
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

        :param eta: [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio

        :type eta:  float
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
                      eta = eta,
                      PI  = PI,
                      TAU = TAU,
                      )

        self.t0 = p.t01
        self.p0 = p.p01

        return p

    def compression(self, eta,
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
            - eta, PI
                - TAU is calculated
            - eta, TAU
                - PI is calculated

        :param eta: [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type eta:  float
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
                          eta = eta,
                          PI  = PI,
                          TAU = TAU,
                          )

        self.t0 = p.t01
        self.p0 = p.p01

        return p

    def expansion(self, eta,
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
            - PI, eta
                - TAU is calculated
            - TAU, eta
                - PI is calculated

        :param eta: [-]  Isentropic efficiency
        :param PI:  [-]  Pressure ratio
        :param TAU: [-]  Temperature ratio

        :type eta:  float
        :type PI:   float
        :type TAU:  float

        :return:    process instance
        """

        k   = self.k(self.t0)
        cp  = self.cp(self.t0)

        p   = expansion(mf  = self.mf,
                        cp  = cp,
                        k   = k,
                        t00 = self.t0,
                        p00 = self.p0,
                        eta = eta,
                        PI  = PI,
                        TAU = TAU,
                        )

        self.t0 = p.t01
        self.p0 = p.p01

        return p

    def heat_addition(self, eta,
                      cp,
                      fuel_mf,
                      fuel_LHV):
        """
        Constant pressure heat addition
        -------------------------------

        Assumptions:
        - Perfect heat addition
        - Constant pressure

        :param eta:      Isentropic efficiency
        :param cp:       Specific heat of gas during heat addition
        :param fuel_mf:  Fuel mass flow
        :param fuel_LHV: Fuel Lower Heating Value (heat of combustion)
        """

        p = combustion(mf       = self.mf,
                       cp       = cp,
                       t00      = self.t0,
                       p00      = self.p0,
                       fuel_mf  = fuel_mf,
                       fuel_LHV = fuel_LHV,
                       eta      = eta)

        self.t0 = p.t01
        self.p0 = p.p01

        return p


class fuel:
    """
    Fuel class
    """
    def __init__(self, LHV,
                 mf=None):
        """
        :param LHV: Fuel Lower Heating Value (heat of combustion)
        :param mf:  Fuel mass flow
        """
        self.LHV = LHV
        self.mf = mf


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
