from copy import deepcopy

from huracan.engine import component
from huracan.thermo.fluids import fuel


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
        based on:

        - The heat required by all downstream
          turbines (work which the turbines of the
          engine must subtract from the flow).
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

        mf_min = self.mf_qr(self.Q_min(downstream=self.stream.downstream))

        if not isinstance(self.t01, type(None)):
            mf_t01 = self.mf_dt(dt=self.t01 - gas.t0, gas=gas)
            self.fuel.mf = mf_t01 if mf_t01 > mf_min else mf_min
        elif not isinstance(self.fuel.mf, type(None)):
            self.fuel.mf = self.fuel.mf if self.fuel.mf > mf_min else self.fuel.mf
        else:
            self.fuel.mf = mf_min

        gas += self.fuel

        """Obtain an approximated total temperature at which the combustion process takes place"""
        approx_process_t = deepcopy(gas).heat_addition(eta=self.eta,
                                                       cp=gas.cp(gas.t0),
                                                       fuel_mf=self.fuel.mf,
                                                       fuel_LHV=self.fuel.LHV).t01

        return gas.heat_addition(eta=self.eta,
                                 cp=gas.cp(approx_process_t),
                                 fuel_mf=self.fuel.mf,
                                 fuel_LHV=self.fuel.LHV)

    def mf_qr(self, qr):
        """
        Fuel mass flow from heat addition required.
        """
        return qr/(self.eta*self.fuel.LHV)

    def mf_dt(self, dt, gas):
        """
        Fuel mass flow from a required change in total temperature.
        """
        gas_cp = gas.cp(self.t01)       # Heat addition happens at high temperature
        return dt*gas.mf*gas_cp/(self.eta*self.fuel.LHV - dt*gas_cp)

    def Q_min(self, downstream):
        """
        Obtain the heat required by all downstream turbines.

        Assumptions:
        - A single combustion chamber is used to power all
          downstream turbines, without secondary combustion
          chambers in any of the affluent streams.
          If this is the case, the combustion chambers will
          provide the heat required by each of their common
          turbines (and so twice the amount needed).
          For now, it is wise to ensure any secondary combustion
          chambers do not have shared turbines with the main one.

        :type downstream: list of stream

        :return: Heat required by all downstream turbines.
        """
        Qr = []
        for stream in downstream:
            for c in stream.components:
                if isinstance(c, turbine):
                    Qr.append(c.w_r())
        return sum(Qr)

    def Q_dt(self, dt, gas):
        """
        Heat required to raise the temperature of the gas
        flow to a certain total temperature.
        """
        gas_cp = gas.cp(self.t01)       # Heat addition happens at high temperature
        return dt*gas.mf*gas_cp

    def Q_mf(self):
        """
        Heat from the combustion of a fuel with a certain
        mass flow.
        """
        return self.eta*self.fuel.mf*self.fuel.LHV


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
    pass
