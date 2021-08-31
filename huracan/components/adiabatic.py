from huracan.engine import component


class intake(component):
    """
    Intake
    ------

    Airflow fed directly to engine.
    """
    def tf(self, gas):
        return gas.absolute()


class inlet(component):
    """
    Inlet
    -----

    Adiabatic diffusion.
    """
    def __init__(self,
                 eta=None,
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

        assert not isinstance(eta, type(None)) or not isinstance(PI, type(None)) or not isinstance(TAU, type(None))

    def tf(self, gas):
        return gas.diffusion(eta=self.eta, PI=self.PI, TAU=self.TAU)


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


class nozzle(component):
    """
    Nozzle
    ------

    Adiabatic expansion.
    """
    def __init__(self,
                 eta,
                 PI=None
                 ):
        """
        :type eta: float
        :type PI:  float
        """
        self.eta = eta
        self.PI  = PI

        self.choked = False

    def tf(self, gas):
        return gas.expansion(eta=self.eta, PI=self.pi(gas), TAU=None)

    def pi(self, gas):
        """
        Nozzle pressure ratio.

        If the nozzle pressure ratio is not provided, it is set as
        the ratio between the gas total pressure before the nozzle
        and the ambient pressure.
        If the inverse of the nozzle pressure ratio is larger than
        the critical inverse pressure ratio, the flow is choked and
        the nozzle pressure ratio will not exceed the critical pressure
        ratio.
        """
        inv_PI = gas.p0/gas.p_0 if isinstance(self.PI, type(None)) else 1/self.PI

        if inv_PI > self.inv_pi_crit(gas):
            PI = 1/self.inv_pi_crit(gas)
            self.choked = True
        else:
            PI = 1/inv_PI

        return PI

    def inv_pi_crit(self, gas):
        """
        Inverse critical pressure ratio.

        Ratio of the pressure **before** the inlet over that
        **after** the inlet (inversely to the widely used pressure
        ratio), starting from which supersonic flow happens in the
        expansion process, causing the nozzle to become choked.

        With a choked nozzle the expansion of the gas is incomplete,
        with a maximum total pressure ratio in the nozzle equal to

            1/PI_crit

        """
        k = gas.k(gas.t0)
        return 1/(1-1/self.eta*((k-1)/(k+1)))**(k/(k-1))
