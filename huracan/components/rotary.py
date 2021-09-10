# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0


from huracan.engine import component


class compressor(component):
    """
    Compressor
    ----------

    Adiabatic compression.
    """
    def __init__(self,
                 eta,
                 PI=None,
                 TAU=None):
        """
        :type eta: float
        :type PI:  float
        :type TAU: float
        """
        self.eta = eta
        self.PI  = PI
        self.TAU = TAU

    def tf(self, gas):
        return gas.compression(eta=self.eta, PI=self.PI, TAU=self.TAU)


class turbine(component):
    """
    Turbine
    -------

    Adiabatic expansion.
    """
    def __init__(self,
                 eta,
                 PI=None,
                 TAU=None):
        """
        :type eta: float
        :type PI:  float
        :type TAU: float
        """
        self.eta = eta
        self.PI  = PI
        self.TAU = TAU

    def tf(self, gas):
        """
        Before runtime, if no total pressure or temperature
        ratio has been provided, a minimum total temperature
        ratio is calculated.
        This temperature ratio is that required to power the
        work exerting components in the turbine's shaft.
        """
        if isinstance(self.PI, type(None)) and isinstance(self.TAU, type(None)):
            t00 = self.stream.gas.t0
            t01 = self.stream.gas.t0 - self.shaft.w_r()/(self.stream.gas.mf*self.stream.gas.cp(t00))
            self.TAU = t01/t00

        return gas.expansion(eta=self.eta, PI=self.PI, TAU=self.TAU)

    def w_r(self):
        return self.shaft.w_r()


class screw(component):
    """
    Screw
    -----

    Mechanical device to turn rotational to axial motion.
    """
    def __init__(self,
                 eta,
                 PI=None,
                 TAU=None):
        """
        :type eta: float
        :type PI:  float
        :type TAU: float
        """
        self.eta = eta
        self.PI  = PI
        self.TAU = TAU


class fan(screw):
    """
    Fan
    ---

    Fundamental differences with a propeller:
    - Disk loading.
    - Fan shroud.
    - Bypass flow.
    """

    def __init__(self,
                 eta,
                 PI=None,
                 TAU=None):
        """
        :type eta: float
        :type PI:  float
        :type TAU: float
        """
        super().__init__(eta=eta,
                         PI= PI,
                         TAU=TAU)

    def tf(self, gas):
        return gas.compression(eta=self.eta, PI=self.PI, TAU=self.TAU)


class prop(screw):
    """
    Propeller
    ---------
    """
    def __init__(self,
                 eta,
                 w,
                 PI=None,
                 TAU=None):
        """
        :param w:  [W] Propeller break power

        :type eta: float
        :type w:   float
        :type PI:  float
        :type TAU: float
        """
        super().__init__(eta=1,
                         PI=PI,
                         TAU=TAU)
        self.w        = w
        self.eta_prop = eta

    def thrust(self, v0):
        return self.w*self.eta_prop/v0

    def tf(self, gas):
        p = gas.compression(eta=self.eta, PI=self.PI, TAU=self.TAU)   # Placeholder
        p.w = self.w
        return p


class propfan(prop):
    """
    Propfan
    -------

    Fundamental difference with a propeller:
    - Disk loading.
    """
