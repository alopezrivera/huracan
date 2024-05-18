# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan utilities
-----------------
"""

import re
import sys
import inspect

from matplotlib.colors import to_hex, to_rgba


def join_set_distance(a, b, d):
    return a + ' '*(d - len(a)) + b


def setattr_namespace(o, namespace):
    """
    Set all variables declared in a namespace as as attributes
    of a class instance.
    ---

    1. Obtain list of module names
    2. Get namespace variables
       - Discard all variables with names starting and ending with '_'
    3. Create a dictionary of namespace variable names and values
    4. Set namespace variables as attributes of the input object
       - Given class instance _o_ will not set as attribute of itself
       - The parent class of _o_ will not be set as an attribute of _o_
         if present in the provided namespace.

    :param o: Instance of any given class.
    :param namespace: A given namespace.
                      - locals()
                      - globals()

    :type o: object
    :type namespace: dict
    """
    # List of module names
    _mods_ = list(set(sys.modules) & set(namespace))
    # List of function arguments
    _args_ = setattr_namespace.__code__.co_varnames
    # Get namespace variables:
    #    List of local variables which are not special variables nor module names
    keys = [key for key in namespace.keys() if (key[0] != '_' and key[-1] != '_') and key not in _mods_]
    # Dictionary of namespace variable names and values
    vars = {key: namespace[key] for key in keys}
    for key, value in vars.items():
        if not type(value) == type(o)\
                and not isinstance(o, value if inspect.isclass(value) else type(value)):  # Avoid _o_, parent of _o_
            # Set namespace variables as attributes of the input object
            setattr(o, key, value)


class markers:
    """
    Markers class
    -------------
    """
    circle          = "o"
    x               = "x"
    thin_diamond    = "d"
    triangle_down   = "v"
    pentagon        = "p"
    vline           = "|"
    hline           = "_"
    # Decent
    point           = "."
    square          = "s"
    plus            = "+"
    triangle_up     = "^"
    triangle_left   = "<"
    triangle_right  = ">"
    tri_down        = "1"
    tri_up          = "2"
    tri_left        = "3"
    tri_right       = "4"
    octagon         = "8"
    hexagon1        = "h"
    hexagon2        = "H"
    diamond         = "D"
    tickleft        = 0
    tickright       = 1
    tickup          = 2
    tickdown        = 3
    caretleft       = 4
    caretright      = 5
    caretup         = 6
    caretdown       = 7
    caretleft_base  = 8
    caretright_base = 9
    caretup_base    = 10
    caretdown_base  = 11
    # Wonky tier
    plus_filled     = "P"
    star            = "*"
    # Garbage tier
    pixel           = ","

    # Icompatible
    incompatible    = [x]

    def __init__(self, hollow=False, plotter='plot'):
        self.hollow  = hollow
        self.plotter = plotter

        assert self.plotter in ['plot', 'scatter'], \
            "Plotter must be either 'plot' (for plt.plot, ax.scatter) or 'scatter' (plt.scatter)"

    def __getitem__(self, item):

        special = r'^__(.*?)\__$'

        m       = {k: markers.__dict__[k] for k in markers.__dict__.keys() if (self.hollow and k not in self.incompatible) or not self.hollow}
        keys    = [k for k in m.keys() if not re.match(special, k)]
        marker  = {'marker': m[keys[item]]}

        # FIXME: hollow markers disappear
        if self.hollow:
            if self.plotter == 'scatter':
                marker['mfc'] = 'white'
            else:
                marker['facecolors'] = 'white'

        return marker


def delta(color, factor, fmt='hex'):
    """
    Darker or lighten the input color by a percentage of
    <factor> ([-1, 1]) of the color spectrum (0-255).

    :param fmt:    Output format: 'hex' or 'rgb'.
    :param factor: [-1, 1] Measure in which the color will be modified.

    :type color:   list of int or string
    :type factor:  float
    :type fmt:     string
    """

    assert isinstance(color, list) or isinstance(color, tuple) or isinstance(color, str)

    if isinstance(color, list) or isinstance(color, tuple):
        c_mod = [min(max(0, i + factor), 1) for i in color]
    elif isinstance(color, str):
        c_mod = [min(max(0, i + factor), 1) for i in to_rgba(color, 1.0)]

    if fmt == 'hex':
        return to_hex(c_mod)
    elif fmt == 'rgb':
        return c_mod
    

def colorscheme_one():
    custom = ["darkred",
              "#1f8fff",
              "#FF8F1F",
              "#00C298",
              "#FFBD00",
              "#00FFC4",
              "#FF003B"]
    tableau = ['tab:blue',
               'tab:orange',
               'tab:green',
               'tab:red',
               'tab:purple',
               'tab:brown',
               'tab:pink',
               'tab:gray',
               'tab:olive',
               'tab:cyan']
    return custom + tableau
