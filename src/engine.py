import re
import numpy as np
from copy import deepcopy

from src.thermo.processes import process


class component:
    def __sub__(self, other):
        if isinstance(other, component):
            s = stream()-other
            return s

    def __call__(self, gas):
        p = self.tf(gas)
        for k, v in p.__dict__.items():
            setattr(self, k, v)


class shaft:
    def __init__(self, *args, eta):
        self.eta = eta
        self.components = list(args)

        for c in args:
            c.shaft = self

    def w_exerting_machinery(self):
        """
        Work exerting machinery.
        """
        return [c for c in self.components if c.__class__.__name__ in ['fan',
                                                                       'compressor']]

    def w_r(self):
        """
        Obtain the work required by the
        components which exert work on the
        gas (fan, compressors).
        """
        wem  = self.w_exerting_machinery()

        assert all([hasattr(c, 'w') for c in wem]), \
            "The shaft's work exerting components do not have " \
            "a work attribute: ensure the streams to which each " \
            "belongs have been run up to the respective work " \
            "exerting component."

        work = np.array([c.w for c in wem])
        etas = np.array([c.shaft.eta for c in wem])
        return np.sum(work*etas)


class stream:
    def __init__(self, gas=None):
        """
        :type gas: gas
        """
        self.components = []
        self.stream_id  = 0

        if not isinstance(gas, type(None)):
            self.gas = gas

    # def aux(self):
    #     """
    #     Create stream
    #
    #     :param args: list of components in a stream in sequential order
    #     :type  args: list of component
    #     """
    #     self.components = list(args)
    #     self.stream_id = 0
    #
    #     for c in args:
    #         c.stream = self

    def __sub__(self, other):
        if isinstance(other, component):
            self.components.append(other)
            other.stream = self
            return self
        if isinstance(other, stream):
            pass
        if isinstance(other, system):
            system.parent(self)

    def __rsub__(self, other):
        if isinstance(other, stream):
            pass

    def __mul__(self, other):
        pass

    def __call__(self, gas):
        self.gas = gas
        return self

    def run(self):

        assert hasattr(self, 'gas'), 'stream does not have a gas attribute.'

        for c in self.components:
            c(self.gas)
            c.stage = self._stage_name(c)

    def stages(self):
        return [c.stage for c in self.components]

    def _n_instances(self, comp):
        """
        Calculate the number of instances of a given component
        in the stream instance and return:
        - n=0: '' (empty string)
        - n>0: str(n)

        If n=1, the stage name of the first component instance
        will be changed to add 0 after its stage code.
        Thus, if a there is a single instance of a component
        with stage code <code>, its stage name will be
            <code>
        while if there are n instances, their stage names will be
            <code>0
            <code>1
              ''
            <code>n

        :type comp: component
        """
        n = 0
        # calculate n

        if n == 1:
            self.components[0].stage += str(0)

        return '' if n == 0 else str(n)

    def _stage_name(self, c):
        code = c.__class__.__name__[0] + self._n_instances(c)
        return str(self.stream_id) + code


class system:
    def __init__(self, obj1, obj2):
        """
        Create a system from two objects.

        :type obj1: stream or system
        :type obj2: stream or system
        """
        self.parents = [obj1, obj2]
        self.stream  = obj1-obj2

    def __sub__(self, other):
        if isinstance(other, component):
            return self.stream-other
        if isinstance(other, stream):
            return self
        if isinstance(other, system):
            pass

    def __mul__(self, other):
        pass

    def __call__(self, suppress_output):
        pass

    def _parent(self, obj):
        """
        Set input object as parent of the
        system instance.

        :type obj: stream or system
        """
        self.parents.append(obj)

    def _append(self):
        pass


if __name__ == '__main__':
    from src.thermo.gas import gas
    from src.thermo.fuel import fuel
    from src.components import intake, inlet, compressor, combustion_chamber, turbine, nozzle

    mf = 700
    m = 0.6
    t = 288
    p = 101325
    fr = 0

    fuel = fuel(LHV=43e6)

    g = gas(mf=mf,
            cp=lambda T: 1150 if T > 600 else 1000,
            k=lambda T: 1.33 if T > 600 else 1.4,
            m=m, t_0=t, p_0=p)

    i  = inlet(0.95)
    c  = compressor(0.9, 14)
    cc = combustion_chamber(fuel, 0.98)
    t  = turbine(0.9)

    shft = shaft(c, t, eta=0.8)

    def r_stream_gas_input():
        strm   = i-c     ;    strm(g).run()
        strm_g = g-i-c   ;    strm_g.run()


    strm = g-i-c  #-cc-t-n
    strm.run()

    # sstm =