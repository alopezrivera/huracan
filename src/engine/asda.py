class stage:

    @classmethod
    def concatenate(cls, assembly_prior, assembly_posterior):
        """
        Concatenate two stages or a cycle and a stage into a
        single cycle.

        :param assembly_prior:
        :param assembly_posterior:

        :type assembly_prior: stage or cycle
        :type assembly_posterior: stage or cycle

        :return:
        """

        assembly_posterior.mf = assembly_prior.mf

        return cycle(assembly_prior, assembly_posterior)

    def __init__(self, code, component):
        """
        :param code:      Stage code name
        :param component: Cycle component

        :type code:       str
        :type component:
        """
        self.code      = code
        self.component = component
        self.mf        = component.mf

    def __sub__(self, other):
        """
        Cycle creation operator: <stage> - <other>

        :param other: Stage or cycle to be combined in a cycle
                      with the current stage.

        :type other:  stage or cycle

        :return:      Cycle object
        """
        return self.concatenate(self, other)

    def __rsub__(self, other):
        """
        Cycle creation operator: <other> - <stage>

        :param other: Stage or cycle to be combined in a cycle
                      with the current stage.

        :type other:  stage or cycle

        :return:      Cycle object
        """
        return self.concatenate(self, other)


class cycle:

    def __init__(self, assembly_prior, assembly_posterior):
        if isinstance(assembly_prior, cycle):
            assembly_prior + assembly_posterior
        else:
            pass

    def __add__(self, other):
        """
        Cycle stage addition operator: <cycle> + <stage>

        :param other: stage

        :return: Cycle object
        """
        setattr(self, other.code, other)


if __name__ == "__main__":

    class z:
        def __init__(self, mf):
            self.mf = mf

    y = z(1230)
    x = z(1459)

    a = stage('01', y)
    b = stage('02', x)
    c = a-b
