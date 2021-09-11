# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
System power sinks
------------------
"""

from huracan.engine import component


class electrical_system(component):
    """
    Aircraft electrical system
    --------------------------
    """
    def __init__(self,
                 w,
                 eta_g=1,
                 eta_c=1):
        """
        :param w:     [W] Power required by the electrical system.
        :param eta_g: [-] Efficiency of the electrical generator attached
                          to the turbine.
        :param eta_c: [-] Efficiency of the electrical power distribution
                          grid of the aircraft.
        """
        self.w_r = w/eta_g/eta_c
