# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0

"""
Engine power plants
-------------------
"""


class plant:
    """
    Plant
    -----

    Engine power plant class. From it all children power plant 
    classes inherit the Q_min method, which returns the 
    heat required to power the rotary components of the engine.
    """
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
                if c.__class__.__name__ == 'turbine':
                    Qr.append(c.w_r())
        return sum(Qr)
