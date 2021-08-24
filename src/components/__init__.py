import re
from copy import deepcopy

from src.thermo.processes import process


class stage:
    pass


class cycle:

    def _append(self, other, stage_name=None):
        """
        Append a component to the cycle.
        If not provided, the stage name is
        generated ensuing those of the
        components already present in the
        cycle.

        :type stage_name: str
        """
        s = stage()
        s.component = other
        setattr(self, stage_name if not isinstance(stage_name, type(None)) else self._stage_name(other), s)

    def _stage_name(self, element, nested=False):
        """
        Return stage name for a given component
        of a cycle instance.

        :type element: component
        :type nested: bool

        :return: Stage name string
        """

        start = 's00'

        cls         = element.__class__.__name__
        # Use regex to match stage names in the form 's<n><n><n>' where <n> may be any numeric character
        stg_names   = [a for a in self.__dict__.keys() if re.match(r'[s]\d{1,3}', a)]
        stg_classes = [v.__class__.__name__ for k, v in self.__dict__.items() if re.match(r'[s]\d{1,3}', k)]

        base = start if len(stg_names) == 1 else stg_names[-1]
        if cls in ['intake', 'inlet'] or nested:
            # Nested stage codes
            stg_name = base[:2] + str((int(base[-1]) + 1) if len(base) > 2 else 1)
        else:
            stg_name = base[0] + str(int(base[1]) + 1)

        return stg_name

    def __init__(self, gas=None):

        if not isinstance(gas, type(None)):
            self.gas = gas

        self._append(intake(), 's00')           # Ambient absolute temperature and pressure stage

    def __sub__(self, other):
        """
        Cycle expansion operator: <cycle> - <component/cycle>

        :type other: component or cycle

        :return:     cycle instance
        """

        if isinstance(other, component):
            self._append(other)
            return self
        # elif isinstance(other, cycle):
        #     stage = 'a'
        #     setattr(other, stage, self)
        #     return other
        # elif isinstance(other, diversion):
        #     pass
        # elif isinstance(other, secondary_airflow):
        #     pass

    def run(self):
        """
        Run all transfer functions in the cycle.
        """

        assert hasattr(self, 'gas'), 'This cycle instance does not have a gas attribute. ' \
                                     'Set a gas attribute for the cycle instance'

        stages      = [v for k, v in self.__dict__.items() if re.match(r'[s]\d{1,3}', k)]
        stage_names = [k for k, v in self.__dict__.items() if re.match(r'[s]\d{1,3}', k)]

        # Run
        for i in range(len(stages)):
            stages[i].process = stages[i].component(self.gas)
            setattr(self, stage_names[i], stages[i])

        # Cycle values
        self.t0 = self._t0()
        self.p0 = self._p0()
        self.S  = self._S()

    def __call__(self, gas=None):
        """
        Run a cycle.

        :type gas: gas
        """

        if not isinstance(gas, type(None)):
            gas-self

        self.run()

        return self

    def stage_loop(self, f):
        """
        AFTER RUNNING THE CYCLE each stage
        consists of a process instance
        containing all calculated values in
        that stage.

        This function loops through all stages
        and returns a list with the results of
        the input function f on each stage.

        :type f: (process) -> any

        :return: map
        """

        stages = [v for k, v in self.__dict__.items() if re.match(r'[s]\d{1,3}', k)]

        r = []
        for stage in stages:
            r.append(f(stage.process))

        return r

    def _t0(self):
        """
        Return a vector containing the total
        temperature at each stage of the cycle.
        """
        return self.stage_loop(lambda p: getattr(p, 't01' if hasattr(p, 't01') else 't0'))

    def _p0(self):
        """
        Return a vector containing the total
        pressure at each stage of the cycle.
        """
        return self.stage_loop(lambda p: getattr(p, 'p01' if hasattr(p, 'p01') else 'p0'))

    def _S(self):
        """
        Return a vector containing the
        entropy at each stage of the cycle.
        """
        pass


class component:

    def __sub__(self, other):
        """
        Cycle creation operator: <component> - <component>

        :type other: component

        :return:     cycle instance
        """

        c = cycle()
        c-self-other

        return c

    def __call__(self, gas):
        return self.tf(gas)


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
                 nu,
                 PI=None,
                 TAU=None):
        self.nu = nu
        self.PI = PI
        self.TAU = TAU

    def tf(self, gas):
        return gas.diffusion(nu=self.nu, PI=self.PI, TAU=self.TAU)


class compressor(component):
    """
    Compressor
    """
    def __init__(self,
                 nu,
                 PI=None,
                 TAU=None):
        self.nu = nu
        self.PI = PI
        self.TAU = TAU

    def tf(self, gas):
        return gas.compression(nu=self.nu, PI=self.PI, TAU=self.TAU)


class turbine(component):
    """
    Turbine
    """
    def __init__(self,
                 nu,
                 PI=None,
                 TAU=None):
        self.nu = nu
        self.PI = PI
        self.TAU = TAU

    def tf(self, gas):
        return gas.compression(nu=self.nu, PI=self.PI, TAU=self.TAU)


class nozzle(component):
    pass
