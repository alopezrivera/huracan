class engine:
    """
    Engine class
    """
    def __init__(self, assembly_inner, assembly_outer):
        """
        Create engine.

        "Inner-to-outer" component hierarchy:
            - assembly_inner -> inner components
            - assembly_outer -> outer components

        In terms of components, this means that for a
        conventional turbofan engine:
            - assembly_inner contains:
                - High pressure compressor
                - Combustion chamber
                - High pressure turbine
            - assembly_outer contains:
                - Fan
                - Low pressure compressor
                - Low pressure turbine

        A three-spool turbofan engine would be built as
        follows:

            shaft1 = shaft(HPC2, CC, HPT2)
            shaft2 = shaft(HPC1, HPT1)
            shaft3 = shaft(fan, LPC, LPT)

            engine = shaft1 | shaft2 | shaft3
                     \_____________/
                            |
                        engine obj                -> 2 spool engine
                     \______________________/
                                |
                            engine obj            -> 3 spool engine

        :param assembly_inner: Structural component 1
        :param assembly_outer: Structural component 2
        """
        pass


class shaft:
    """
    Shaft class
    """
    @classmethod
    def _engine(cls, assembly_inner, assembly_outer):
        """
        Create engine from two structural components.

        :param assembly_inner: Structural component 1
        :param assembly_outer: Structural component 2

        :type assembly_inner: shaft or engine
        :type assembly_outer: shaft or engine

        :return: Engine object composed of structural components 1 and 2
        """
        assert isinstance(assembly_inner, shaft) or isinstance(assembly_outer, engine)
        return engine(assembly_inner, assembly_outer)

    def __xor__(self, other):
        """
        Engine creation operator: <shaft> | <other>

        :type other: shaft or engine
        """
        return self._engine(self, other)

    def __rxor__(self, other):
        """
        Engine creation operator: <other> | <shaft>

        :type other: shaft or engine
        """
        return self._engine(self, other)
