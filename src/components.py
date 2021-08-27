from src.engine import component
from src.thermo.fuel import fuel


class intake(component):
    """
    Intake

    Airflow fed directly to engine
    """
    def tf(self, gas):
        return gas.absolute()


class inlet(intake):
    """
    Inlet
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
        return gas.diffusion(eta=self.eta, PI=self.PI, TAU=self.TAU)


class compressor(component):
    """
    Compressor
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

        if isinstance(PI, type(None)) and isinstance(TAU, type(None)):
            gas = gas
            t00 = gas.t0
            t01 = gas.t0 - self.shaft.w_r/(gas.mf*gas.cp(t00))
            self.TAU = t01/t00
        else:
            self.PI  = PI
            self.TAU = TAU

    def tf(self, gas):
        return gas.expansion(eta=self.eta, PI=self.PI, TAU=self.TAU)


class combustion_chamber(component):
    """
    Combustion chamber
    """
    def __init__(self,
                 fuel,
                 eta,
                 t01=None,
                 ):
        """
        The total pressure and temperature
        after the combustion chamber are calculated
        based on

        - The work which the turbines of the engine
          must subtract from the flow.
          -> Heat addition so as to feed the known
             energy use.

        - The fuel mass flow (attribute of
          the input fuel class instance) if provided,
          if the heat added if equal or larger than
          that required by the turbines.
          -> Heat addition from input fuel mass flow

        - The total temperature of the gas
          at the exit of the combustion chamber t01
          if provided, if the heat added if equal or
          larger than that required by the turbines.
          -> Heat addition so as to reach t01

        :param fuel: Instance of fuel class.
        :param eta:  Isentropic efficiency.
        :param t01:  Temperature after the combustion chamber.

        :type fuel:  fuel
        :type t01:   float
        """

        self.fuel = fuel
        self.eta  = eta
        self.t01  = t01

    def tf(self, gas):
        """
        At the time of execution, the fuel mass flow is
        determined based on:

        - The heat required by the turbines (minimum mass flow)
        - The fuel mass flow if provided, if larger than the
          minimum mass flow
        - The total temperature of the gas at the exit of
          the combustion chamber t01 if provided, if the
          required mass flow for it is larger than the
          minimum mass flow
        """

        # mf w
        # mf dt if dt

        if not hasattr(fuel, 'mf'):
            fuel.mf = self.fmf()
        elif not isinstance(self.t01, type(None)):
            pass
        else:
            pass

        return gas.heat_addition(eta=self.eta, fuel_mf=self.fuel.mf, fuel_LHV=self.fuel.LHV)

    def mf_w(self, w):
        """
        :type w: float
        """
        return w/(self.eta*self.fuel.LHV)

    def mf_dt(self, dt):
        """
        dt = t01 - previous t01
        mf = gas.mf
        cp = gas.cp(combustion t)

        dt*mf*cp/(nu_cc*fuelLHV)
        """
        return dt


class turbine(component):
    """
    Turbine
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
        self.PI = PI
        self.TAU = TAU

    def tf(self, gas):
        return gas.expansion(eta=self.eta, PI=self.PI, TAU=self.TAU)


class nozzle(component):
    pass
