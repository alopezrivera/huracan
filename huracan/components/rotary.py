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

    def tf(self, gas):
        return gas.compression(eta=self.eta, PI=self.PI, TAU=self.TAU)


class fan(screw):
    """
    Fan
    ---

    Fundamental difference with a propeller: disk loading.
    """
    pass


class prop(screw):
    """
    Propeller
    ---------

    Fundamental difference with a propeller: disk loading.
    """
    pass


class propfan(screw):
    """
    Propfan
    -------

    Fundamental difference with a propeller: disk loading.
    """
    pass
