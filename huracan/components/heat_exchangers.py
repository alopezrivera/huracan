# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
System heat exchangers
----------------------
"""

from huracan.engine import component


class heat_sink(component):
    """
    Heat sink
    ---------
    """
    def __init__(self,
                 eta,
                 PI=1
                 ):
        """
        :param eta:   Isentropic efficiency.
        """

        self.eta = eta
        self.PI  = PI

    def tf(self, gas):

        assert hasattr(self, 'Q_out'), \
            'Heat sink children component has no heat removed method implemented.'

        return gas.heat_exchange(eta=self.eta,
                                 PI=self.PI,
                                 cp=gas.cp(gas.t0),
                                 Q_ex=-self.Q_out(gas),
                                 )


class intercooler(heat_sink):           # TODO: implement coolant-based intercooling
    """
    Intercooler
    -----------
    """
    def __init__(self,
                 Q_out,
                 eta):
        """
        :param Q_out: Heat removed by the intercooler.
        :param eta:   Isentropic efficiency.
        """
        super().__init__(eta=eta)

        self.Q_out = lambda _: Q_out

    def Q_out(self, gas):
        """
        Heat removed by the intercooler.

        Parameters:
        * Gas
        * Coolant
        * Coolant mass flow
        * Contact area
        * Thermal exchange efficiency
        """
        pass
