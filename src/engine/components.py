from src.thermo.fluids import gas


class cycle:

    def __sub__(self, other):
        """
        Component addition operator: <cycle> - <component/cycle>

        :param other: Component or cycle

        :type other:  component or cycle

        :return:      Cycle object
        """
        # return self.concatenate(self, other)
        if isinstance(other, component):
            c = cycle()
            stage1 = 'a'
            stage2 = 'a'
            setattr(c, stage1, other)
            setattr(c, stage2, self)
        elif isinstance(other, cycle):
            stage = 'a'
            setattr(other, stage, self)
        elif isinstance(other, diversion):
            pass
        elif isinstance(other, secondary_airflow):
            pass


class component:

    def __sub__(self, other):
        """
        Cycle creation operator: <component> - <component>

        :param other: Component

        :type other:  component

        :return:      Cycle object
        """

        c = cycle()
        stage1 = 'a'
        stage2 = 'a'
        setattr(c, stage1, self)
        setattr(c, stage2, other)


class inlet(component):
    """
    COMPONENT: INLET
    """
    def __init__(self,
                 gas,
                 v0,
                 pi,
                 nu):
        self.v0 = v0
        self.nu = nu
        self.pi = pi

        g = gas(cp, k)

    def _p(self, p):
        return expansion_p(self.pi, p)

    def _t(self, t):
        return t


class compressor(component):
    pass


class turbine(component):
    pass
