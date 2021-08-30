import numpy as np

from mpl_plotter import figure
from mpl_plotter.two_d import line, scatter, comparison
from mpl_plotter.color.schemes import colorscheme_one
from mpl_plotter.color.functions import delta

from alexandria.shell import print_color, print_result
from alexandria.data_structs.string import join_set_distance

from huracan.constants import R

"""
Huracan engine architecture
"""


class component:
    """
    Component
    """
    def __sub__(self, other):
        """
        Stream creation operator: <component> - <component>
        """
        if isinstance(other, component):
            s = stream()-other
            return s

    def __call__(self, gas):
        """
        Component transfer function execution
        """
        p = self.tf(gas)
        for k, v in p.__dict__.items():
            if k[-2:] == '01':
                k = k[0] + '0'
            setattr(self, k, v)


class shaft:
    """
    Shaft
    """
    def __init__(self, *args, eta):
        """
        :param args: list of components connected by the shaft.
        :param eta:  mechanical efficiency of the shaft.

        :type args:  list of component
        :type eta:   float
        """
        self.eta = eta
        self.components = list(args)

        for c in args:
            c.shaft = self

    def w_exerting_machinery(self):
        """
        Return a list of all components in the shaft
        which exert work on the flow. That is, instances
        of the fan and compressor classes.
        """
        return [c for c in self.components if c.__class__.__name__ in ['fan',
                                                                       'compressor']]

    def w_r(self):
        """
        Obtain the work required by the components which
        exert work on the gas (fan, compressors).
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
    """
    Stream
    """
    def __init__(self, gas=None):
        """
        :type gas: gas
        """
        self.stream_id = 0
        self.components = []
        self.downstream = [self]

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
            other.downstream = self.downstream
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

    def run(self, log=True):
        """
        Execute the transfer functions of all components in the stream
        on the instance's gas class instance.
        """
        assert hasattr(self, 'gas'), 'stream does not have a gas attribute.'

        for c in self.components:
            c(self.gas)
            c.stage = self._stage_name(c)

        if log:
            for c in self.components:
                section_name = join_set_distance(c.stage, c.__class__.__name__.capitalize().replace("_", " "), 6)
                print_color(section_name, 'green')

                if c.__class__.__name__ == 'nozzle':
                    if c.PI == 1/c.inv_pi_crit(self.gas):
                        print_color('      Choked flow', 'red')

                print_result('       T0', c.t0, '[K]')
                print_result('       p0', c.p0, '[Pa]')

    def stages(self):
        """
        Return a list containing the stage name of each
        component in the stream.
        """
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

        for c in self.components:
            if comp is c:
                break
            if comp.__class__.__name__ == c.__class__.__name__ and comp is not c:
                n += 1

        if n == 1:
            for i in range(len(self.components)):
                if comp.__class__.__name__ == self.components[i].__class__.__name__ and not comp is self.components[i]:
                    self.components[i].stage += str(0)

        return '' if n == 0 else str(n)

    def _stage_name(self, c):
        """
        Return the stage name of a component in the stream,
        composed of the stream identification number, a code
        representing its parent class, and a numerical index
        if there are more than 1 components of the same class
        in the stream.
        """
        codes = {'intake':             'it',
                 'inlet':              'il',
                 'fan':                'fn',
                 'compressor':         'c',
                 'combustion_chamber': 'cc',
                 'turbine':            't',
                 'afterburner':        'ab',
                 'nozzle':             'n'
                 }

        code = codes[c.__class__.__name__] + self._n_instances(c)
        return f'{self.stream_id}.{code}'

    def fmf(self):
        """
        Stream fuel mass flow
        """
        fmf = 0
        for c in self.components:
            if hasattr(c, 'fuel') and hasattr(c.fuel, 'mf'):
                fmf += c.fuel.mf
        return fmf

    def t0(self):
        """
        Total temperature vector.
        """
        return np.array([c.t0 for c in self.components])

    def p0(self):
        """
        Total pressure vector.
        """
        return np.array([c.p0 for c in self.components])

    def v0(self):
        """
        Specific total volume vector.
        """
        return np.array([c.t0*R/c.p0 for c in self.components])

    def S(self):
        """
        Specific entropy vector.
        """
        S = lambda t0, p0: 1
        return np.array([S(t0=c.t0, p0=c.p0) for c in self.components])

    def plot_T_p(self,
                 show=False,
                 label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Total pressure
        - Total temperature
        """

        defaults = {'x_label': 'p$_0$ [kPa]',
                    'y_label': 'T$_0$ [K]'}

        further_custom = {**defaults, **kwargs}

        self.plot_cycle_graph(self.p0()/1000, self.t0(),
                              color=color,
                              label=label,
                              show=show,
                              # Further customization
                              x_tick_ndecimals=2,
                              **further_custom)

    def plot_p_v(self,
                 show=False,
                 label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Total specific volume
        - Total pressure
        """

        defaults = {'x_label': 'v$_0$ [m$^3$/n]',
                    'y_label': 'p$_0$ [kPa]'}

        further_custom = {**defaults, **kwargs}

        self.plot_cycle_graph(self.v0(), self.p0()/1000,
                              color=color,
                              label=label,
                              show=show,
                              # Further customization
                              y_tick_ndecimals=2,
                              **further_custom)

    def plot_T_S(self,
                 show=False,
                 label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Specific entropy
        - Total temperature
        """

        defaults = {'x_label': 'S [J/K/n]',
                    'y_label': 'T$_0$ [K]'}

        further_custom = {**defaults, **kwargs}

    def plot_cycle_graph(self,
                         x, y,
                         label,
                         x_label, y_label,
                         color=colorscheme_one()[0],
                         show=False,
                         **kwargs
                         ):
        """
        Cycle plot composed of an MPL Plotter line and scatter plot.

        The default arguments plus any valid MPL Plotter line plotting
        class arguments can be passed to this function.
        """
        if not any([k == 'fig' for k in kwargs.keys()]):
            fig = figure((9, 5))
        else:
            fig = kwargs.pop('fig')

        defaults = {
            # Specifics
            'point_size': 30,
            # Markers
            'marker': 'x',
            # Color
            'color': delta(color, -0.3),
            # Arrangement
            'zorder': 2,
            # Further customization
            'aspect': 1/2,
            'x_tick_number': 10,
            'y_tick_number': 10,
            'demo_pad_plot': True,
        }

        further_custom = {**defaults, **kwargs}

        # Connecting lines
        line(   x=x, y=y,
                # Figure
                fig=fig,
                # Specifics
                line_width=1,
                # Color
                color=color, alpha=0.65,
                # Arrangement
                zorder=1)
        # Stages
        scatter(x=x, y=y,
                # Further customization
                plot_label=label,
                x_label=x_label,
                y_label=y_label,
                show=show,
                **further_custom)


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

    def thrust(self):
        pass

    def efficiency(self):
        pass

    def plot_T_p(self):

        plotters = []
        x        = []
        y        = []

        for stream in self.streams:
            plotters.append(lambda s, x, y: s.plot_cycle_graph(x=x, y=y, lable=None, x_label='', y_label=''))
            x.append(stream.p0())
            y.append(stream.v0())

        comparison(x=x, y=y, f=plotters)

    def plot_p_v(self):

        plotters = []
        x        = []
        y        = []

        for stream in self.streams:
            plotters.append(lambda s, x, y: s.plot_cycle_graph(x=x, y=y, lable=None, x_label='', y_label=''))
            x.append(stream.p0())
            y.append(stream.v0())

        comparison(x=x, y=y, f=plotters)

    def plot_T_S(self):

        plotters = []
        x        = []
        y        = []

        for stream in self.streams:
            plotters.append(lambda s, x, y: s.plot_cycle_graph(x=x, y=y, lable=None, x_label='', y_label=''))
            x.append(stream.p0())
            y.append(stream.v0())

        comparison(x=x, y=y, f=plotters)


if __name__ == '__main__':
    from huracan.thermo.fluids import gas, fuel
    from huracan.components import intake, inlet, compressor, combustion_chamber, turbine, nozzle

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
    n  = nozzle(0.95)

    shft = shaft(c, t, eta=0.8)

    def r_stream_gas_input():
        strm   = i-c     ;    strm(g).run()
        strm_g = g-i-c   ;    strm_g.run()

    strm = g-i-c-cc-t-n
    strm.run()

    # sstm =