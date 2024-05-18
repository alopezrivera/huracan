# SPDX-FileCopyrightText: © 2024 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""
Huracan engine components
-------------------------
"""

from huracan.components.channels import intake, inlet, nozzle, bleed_duct
from huracan.components.rotary import fan, prop, propfan, compressor, turbine
from huracan.components.power.combustion import combustion_chamber, afterburner
from huracan.components.power.sinks import electrical_system
from huracan.components.heat_exchangers import intercooler
