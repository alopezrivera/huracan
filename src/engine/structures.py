from src.engine.engine import engine


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


class diversion:
    pass
