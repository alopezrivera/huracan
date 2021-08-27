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
