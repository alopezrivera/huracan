class fuel:
    """
    Fuel class
    """
    def __init__(self, mf, LHV):
        """
        :param mf:
        :param LHV:
        """
        super().__init__(mf)
        self.LHV = LHV

    def heat(self):
        """
        Constant pressure heat addition
        """
        pass


if __name__ == '__main__':
    f = fuel(mf  = 20,
             LHV = 43e6)
