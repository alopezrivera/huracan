from huracan.engine import component


class power_plant(component):
    """
    Aircraft electrical power plant
    -------------------------------
    """
    def __init__(self,
                 w,
                 eta_g=1,
                 eta_c=1):
        """
        :param w:     [W] Power required by the electrical power plant.
        :param eta_g: [-] Efficiency of the electrical generator attached
                          to the turbine.
        :param eta_c: [-] Efficiency of the electrical power distribution
                          grid of the aircraft.
        """
        self.w_r = w/eta_g/eta_c
