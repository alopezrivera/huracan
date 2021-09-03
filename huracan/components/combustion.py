from copy import deepcopy

from huracan.engine import component
from huracan.components import turbine


class combustor(component):
    """
    Combustor
    ---------

    Constant pressure heat addition.
    """
    def __init__(self,
                 fuel,
                 eta,
                 PI=1,
                 t01=None,
                 ):
        """
        The total pressure and temperature
        after the combustor are calculated
        based on:

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
        self.PI   = PI
        self.t01  = t01

    def tf(self, gas):
        """
        By considering combustion happens at low temperature (that
        of the gas before it enters the combustion chamber), an estimate
        of the total temperature of the gas when it exits the combustion
        chamber is obtained.
        This total temperature is then assumed to be the temperature
        at which the combustion process takes place.
        """

        assert hasattr(self, 'fmf'), \
            'Component incorporating combustor has no fuel mass flow method implemented.'

        self.fmf(gas)

        self.Q = self.fuel.mf*self.eta*self.fuel.LHV      # Heat added to the flow

        approx_process_t = deepcopy(gas).heat_addition(eta=self.eta,
                                                       cp=gas.cp(gas.t0),
                                                       fuel_mf=self.fuel.mf,
                                                       fuel_LHV=self.fuel.LHV).t01

        return gas.heat_addition(eta=self.eta,
                                 PI=self.PI,
                                 cp=gas.cp(approx_process_t),
                                 fuel_mf=self.fuel.mf,
                                 fuel_LHV=self.fuel.LHV)

    def mf_dt(self, dt, gas):
        """
        Fuel mass flow from a required change in total temperature.
        """
        gas_cp = gas.cp(self.t01)       # Heat addition happens at high temperature
        return dt*gas.mf*gas_cp/(self.eta*self.fuel.LHV - dt*gas_cp)


class combustion_chamber(combustor):
    """
    Combustion chamber
    ------------------

    Constant pressure heat addition.
    """
    def __init__(self,
                 fuel,
                 eta,
                 PI=1,
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
        super().__init__(fuel=fuel,
                         eta=eta,
                         PI=PI,
                         t01=t01)

    def fmf(self, gas):
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

    def mf_qr(self, qr):
        """
        Fuel mass flow from heat addition required.
        """
        return qr/(self.eta*self.fuel.LHV)

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


class afterburner(combustor):
    """
    Afterburner or Reheater
    -----------------------

    Constant pressure heat addition.
    """
    def __init__(self,
                 fuel,
                 eta,
                 PI=1,
                 t01=None):
        """
        The total pressure and temperature
        after the afterburner are calculated
        based on:

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
        super().__init__(fuel=fuel,
                         eta=eta,
                         PI=PI,
                         t01=t01)

    def fmf(self, gas):
        """
        At the time of execution, the fuel mass flow is
        determined based on:

        - The fuel mass flow if provided, if larger than the
          minimum mass flow
        - The total temperature of the gas at the exit of
          the combustion chamber t01 if provided, if the
          required mass flow for it is larger than the
          minimum mass flow
        """
        assert not isinstance(self.t01, type(None)) or not isinstance(self.fuel.mf, type(None)), \
            'Afterburner: neither the fuel mass flow nor the temperature t01 after the afterburner have been' \
            'provided. Input either one in the initialization of your afterburner instance to proceed.'

        if not isinstance(self.t01, type(None)):
            self.fuel.mf = self.mf_dt(dt=self.t01 - gas.t0, gas=gas)
        elif not isinstance(self.fuel.mf, type(None)):
            self.fuel.mf = self.fuel.mf

        gas += self.fuel
