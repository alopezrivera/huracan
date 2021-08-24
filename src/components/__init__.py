import re


class cycle:

    @classmethod
    def _concat(cls):
        pass

    def _stage(self, element):
        """
        Return stage name for a given component
        of a cycle instance.
        """

        start = 's0'

        cls         = element.__class__.__name__
        # Use regex to match stage names in the form 's<n><n><n>' where <n> may be any numeric character
        stg_names   = [a for a in self.__dict__.keys() if re.match(r'[s]\d{1,3}', a)]
        stg_classes = [v.__class__.__name__ for k, v in self.__dict__.items() if re.match(r'[s]\d{1,3}', k)]
        stg_number  = stg_classes.count(cls)
        stg_index   = stg_classes.index(cls) if stg_number > 0 else -1

        # n = 0
        # for i in range(stg_number):
        #     if stg_classes[stg_index-i] == cls:
        #         n += 1
        #     else:
        #         break

        base = start if len(stg_names) == 0 else stg_names[-1]
        if cls in ['intake', 'inlet']:
            # Nested stage codes
            stg_name = base + str((int(base[-1]) + 1) if len(base) > 2 else 1)
        else:
            stg_name = base[0] + str(int(base[1]) + 1)

        return stg_name


    def run(self):
        """
        Run all transfer functions in the cycle.
        """
        pass

    def t0(self):
        """
        Return a vector containing the total
        temperature at each stage of the cycle.
        """
        pass

    def p0(self):
        """
        Return a vector containing the total
        pressure at each stage of the cycle.
        """
        pass

    def S(self):
        """
        Return a vector containing the
        entropy at each stage of the cycle.
        """
        pass

    def __init__(self, gas=None):
        if not isinstance(gas, type(None)):
            self.gas = gas

    def __sub__(self, other):
        """
        Cycle expansion operator: <cycle> - <component/cycle>

        :type other: component or cycle

        :return:     cycle instance
        """

        assert hasattr(self, 'gas'), 'This cycle instance does not have a gas attribute. ' \
                                     'Set a gas attribute for the cycle instance'

        if isinstance(other, component):
            stage = self._stage(other)
            setattr(self, stage, other)
            return self
        # elif isinstance(other, cycle):
        #     stage = 'a'
        #     setattr(other, stage, self)
        #     return other
        # elif isinstance(other, diversion):
        #     pass
        # elif isinstance(other, secondary_airflow):
        #     pass

    def __call__(self, gas):
        """
        Run a cycle.

        :type gas: gas
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
        stage1 = 's0'
        stage2 = 's1'
        setattr(c, stage1, self)
        setattr(c, stage2, other)

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
