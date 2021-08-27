class fuel:
    """
    Fuel class
    """
    def __init__(self, LHV, mf=None):
        """
        :param LHV: Fuel Lower Heating Value (heat of combustion)
        :param mf:  Fuel mass flow
        """
        self.LHV = LHV
        self.mf = mf


if __name__ == '__main__':
    f = fuel(mf  = 20,
             LHV = 43e6)
