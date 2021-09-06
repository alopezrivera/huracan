import numpy as np
from copy import deepcopy

from mpl_plotter import figure
from mpl_plotter.two_d import line, scatter, comparison
from mpl_plotter.color.schemes import colorscheme_one
from mpl_plotter.color.functions import delta

from alexandria.shell import print_color, print_result
from alexandria.data_structs.string import join_set_distance

from huracan.constants import R


class component:
    """
    Component
    ---------
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

        # Gas state variables
        for sv in ['V', 'S', 'H']:
            setattr(self, sv, getattr(gas, sv))


class shaft:
    """
    Shaft
    -----
    """
    def __init__(self, *args, eta, eta_gearbox=1):
        """
        :param args: list of components connected by the shaft.
        :param eta:  mechanical efficiency of the shaft.

        :type args:  component
        :type eta:   float
        """
        self.eta         = eta
        self.eta_gearbox = eta_gearbox
        self.components  = list(args)

        for c in args:
            c.shaft = self

    def w_exerting_machinery(self):
        """
        Return a list of all components in the shaft
        which exert work on the flow. That is, instances
        of the fan and compressor classes.
        """
        return [c for c in self.components if c.__class__.__name__ in ['fan',
                                                                       'prop',
                                                                       'propfan',
                                                                       'compressor']]

    def electrical_plants(self):
        return [c for c in self.components if c.__class__.__name__ in ['power_plant']]

    def w_r(self):
        """
        Obtain the work required by the components which
        exert work on the gas (fan, compressors).
        """
        wem = self.w_exerting_machinery()

        assert all([hasattr(c, 'w') for c in wem]), \
            "The shaft's work exerting components do not have " \
            "a work attribute: ensure the streams to which each " \
            "belongs have been run up to the respective work " \
            "exerting component."

        work = np.array([c.w/self.eta_gearbox if c.__class__.__name__ in ['fan', 'prop', 'propfan']
                         else c.w for c in wem])
        etas = np.array([c.shaft.eta for c in wem])
        w_r_m = np.sum(work/etas)                           # Power required by work exerting components

        electrical = self.electrical_plants()               # FIXME: ugly
        w_r_e = sum([c.w_r for c in electrical])            # Power required by all electrical plants

        return w_r_m + w_r_e


class stream:
    """
    Stream
    ------
    """
    def __init__(self,
                 gas=None,
                 parents=None,
                 fr=None):
        """
        :param fr:      Fraction of the gas instance passed
                        to the stream which physically enters
                        the stream.
                        This is useful so the original gas
                        instance can be passed to child streams
                        in a stream diversion process.
                        In this way, the gas attribute of the
                        child streams points to the original
                        stream's gas instance until the moment
                        the child streams are run: at this
                        time, a deep copy of the original gas
                        instance is created, and the mass flow
                        multiplied by _fr_ to reflect the mass
                        flow actually flowing in the child stream.
        :param parents: Parent streams.
                        - If parents includes 2 or more streams,
                          they will be merged at runtime.

        :type gas:     gas
        :type fr:      float
        :type parents: list of stream
        """
        self.stream_id  = [0]
        self.components = []
        self.downstream = [self]

        self.ran = False

        if not isinstance(gas, type(None)):
            self.gas    = gas
        if not isinstance(parents, type(None)):
            self.parents = parents

        # Runtime dictionary
        self.runtime = {}
        if not isinstance(fr, type(None)):
            self.runtime['fr'] = fr

    """
    Operators
    """
    def __call__(self, gas):
        self.gas = gas
        return self

    def __sub__(self, other):
        """
        Stream concatenation operator: <stream> - <component/stream>
        """
        if isinstance(other, component):
            self._add_component(other)
            return self
        if isinstance(other, stream):               # TODO: stream merge
            return self._add_stream(other)

    def _add_component(self, c):
        """
        Component addition
        """
        self.components.append(c)
        c.downstream = self.downstream
        c.stream = self

    def _add_stream(self, s):
        """
        Stream addition
        """
        assert hasattr(self, 'gas') and hasattr(s, 'gas'), 'Both streams must have a gas attribute for' \
                                                           'the stream merge operation to be possible.'

        n = max(self.stream_id[0], s.stream_id[0])  # Get largest stream_id
        self.stream_id[0] = s.stream_id[0] = n      # Set largest stream_id for both merging streams

        merged = stream(parents=[self, s])
        merged.stream_id[0] = n + 1

        if hasattr(self, 'system') and hasattr(s, 'system'):
            self.system = s.system = merged.system = self.system + s.system
            self.system(merged)
        elif hasattr(self, 'system'):
            self.system(s, merged)
        elif hasattr(s, 'system'):
            s.system(self, merged)
        else:
            system(self, s, merged)

        return merged

    def __mul__(self, other):                       # TODO: stream diversion
        """
        Stream diversion operator: <stream> * n     for n: 0 =< float =< 1
        """
        return self._divert(other)

    def _divert(self, fr, names=None):
        """
        Stream diversion
        """

        assert hasattr(self, 'gas'), 'The stream must have a gas attribute for' \
                                     'the stream diversion operation to be possible.'

        main = stream(self.gas, fr=fr, parents=[self])
        div  = stream(self.gas, fr=1-fr, parents=[self])

        # Stream ID
        main.stream_id[0] = self.stream_id[0] + 1
        div.stream_id[0]  = self.stream_id[0] + 1

        # Diverted stream IDs
        if not isinstance(names, type(None)):
            main.stream_id.append(names[0])
            div.stream_id.append(names[1])
        else:
            mf_matrix = np.array([[main.gas.mf * fr,     main],
                                  [div.gas.mf  * (1-fr), div]])
            mf_matrix = mf_matrix[mf_matrix[:, 0].argsort()[::-1]]

            for i in range(mf_matrix[:, 1].size):
                sub_id = 'm' if i == 0 else f's{i}' if i > 1 else 's'
                mf_matrix[i, 1].stream_id.append(sub_id)

        if hasattr(self, 'system'):
            self.system(main, div)
            main.system = div.system = self.system
        else:
            system(self, main, div)

        return main, div

    """
    Utilities
    """
    def stages(self):
        """
        Return a list containing the stage name of each
        component in the stream.
        """
        return [c.stage for c in self.components]

    def _stage_name(self, c):
        """
        Return the stage name of a component in the stream,
        composed of the stream identification number, a code
        representing its parent class, and a numerical index
        if there are more than 1 components of the same class
        in the stream.
        """
        codes = {'fan':                'fn',
                 'prop':               'pr',
                 'propfan':            'pf',
                 'intake':             'it',
                 'inlet':              'il',
                 'compressor':         'cp',
                 'combustion_chamber': 'cc',
                 'turbine':            'tb',
                 'afterburner':        'ab',
                 'nozzle':             'nz'
                 }

        code = codes[c.__class__.__name__] + self._n_instances(c)

        return f'{".".join([str(c) for c in self.stream_id])}.{code}'

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
                if comp.__class__.__name__ == self.components[i].__class__.__name__ and comp is not self.components[i]:
                    self.components[i].stage += str(0)

        return '' if n == 0 else str(n)

    def _log(self):

        d = 9

        for c in self.components:
            section_name = join_set_distance(c.stage, c.__class__.__name__.capitalize().replace("_", " "), d)
            print_color(section_name, 'green')

            if c.__class__.__name__ == 'nozzle':
                if c.choked:
                    print_color(' '*d + 'Choked flow', 'red')
            print_result(' '*(d+1) + 'T0', c.t0, '[K]')
            print_result(' '*(d+1) + 'p0', c.p0, '[Pa]')

    """
    Stream state
    """
    def v_exit(self):
        """
        Flow exit velocity

        Assumptions:
        - If the flow is not choked:
             The thermal energy lost by the gas as it leaves the nozzle
             is transformed into kinetic energy without losses.
        - If the flow is choked:
             The exit velocity is the velocity of sound before the nozzle
             exit.
        """
        t_before_nozzle = self.components[-2].t0

        if self.choked:
            return (self.gas.k(t_before_nozzle)*R*t_before_nozzle)**0.5     # M=1 immediately before nozzle exit
        else:

            assert t_before_nozzle - self.gas.t0 > 0, 'The total temperature of the flow is lower before ' \
                                                      'the nozzle tha outside the engine: this happens due to the ' \
                                                      'compressors not providing enough energy to the flow. You must ' \
                                                      'either increase the pressure ratio of the compressors or ' \
                                                      'decrease the power extracted from the flow to solve the ' \
                                                      'inconsistency.'

            return (2*self.gas.cp(t_before_nozzle)*(t_before_nozzle - self.gas.t0))**0.5    # Heat -> Kinetic energy

    def A_exit(self):
        """
        Nozzle exit area
        """
        return self.gas.mf*R*self.gas.t0/(self.gas.p0*self.v_exit())

    def t0(self):
        """
        Total temperature vector.
        """
        assert self.ran, 'The stream must be run to obtain the total temperature at each stage'

        return np.array([c.t0 for c in self.components])

    def p0(self):
        """
        Total pressure vector.
        """
        assert self.ran, 'The stream must be run to obtain the total pressure at each stage'

        return np.array([c.p0 for c in self.components])

    def V(self):
        """
        Specific volume vector.
        """
        assert self.ran, 'The stream must be run to obtain the specific volume at each stage'

        return np.array([c.V for c in self.components])

    def S(self):                 # TODO: implement
        """
        Specific entropy vector.
        """
        assert self.ran, 'The stream must be run to obtain the specific entropy at each stage'

        return np.array([c.S for c in self.components])

    """
    Stream runtime functions
    """
    def _run(self, log=True):
        """
        Execute the transfer functions of all components in the stream
        on the instance's gas class instance.
        """

        self._runtime()

        assert hasattr(self, 'gas'), 'stream does not have a gas attribute.'

        self.choked = False                                 # FIXME: choked flow implementation is ugly

        for c in self.components:
            c(self.gas)
            c.stage = self._stage_name(c)

            if hasattr(c, 'choked') and c.choked:           # FIXME: ugly
                self.choked = c.choked

        # Indicate stream has been run.
        self.ran = True

        if log:
            self._log()

    def _runtime(self):
        if hasattr(self, 'parents') and len(self.parents) > 1:
            self._merge()

        for k, v in self.runtime.items():
            f = getattr(self, '_'+k)
            f(v)

    def _merge(self):
        if hasattr(self, 'gas'):
            for s in self.parents:
                self.gas += s.gas
        else:
            self.gas = self.parents[0].gas
            for s in self.parents[1:]:
                self.gas += s.gas

    def _fr(self, fr):
        self.gas, _ = fr * deepcopy(self.gas)

    """
    Stream performance analysis
    """
    def _fmf(self):
        """
        Stream fuel mass flow
        """
        fmf = 0
        for c in self.components:
            if hasattr(c, 'fuel') and hasattr(c.fuel, 'mf'):
                fmf += c.fuel.mf
        return fmf

    def _thrust(self):
        """
        Flow thrust

        If the flow is choked, the expansion of the gas contributes to the thrust of the flow.
        """

        if any([c.__class__.__name__ in ['prop', 'propfan'] for c in self.components]):
            propellers = [c for c in self.components if c.__class__.__name__ in ['prop', 'propfan']]
            prop_thrust = sum([prop.thrust(self.gas.v_0) for prop in propellers])
        else:
            prop_thrust = 0

        if self.choked:
            return prop_thrust + self.gas.mf * (self.v_exit() - self.gas.v_0) + self.A_exit() * (
                        self.gas.p0 - self.gas.p_0)
        else:
            return prop_thrust + self.gas.mf * (self.v_exit() - self.gas.v_0)

    def _sfc(self):
        """
        Specific fuel consumption
        """
        return self.fmf() / self.thrust()

    # def Q_in(self):               #TODO: verify and implement efficiency calculations
    #     """
    #     Heat provided to the flow.
    #     """
    #     q_provided = 0
    #     for c in self.components:
    #         if c.__class__.__name__ == 'combustion_chamber':
    #             q_provided += c.Q
    #     return q_provided
    #
    # def W_req(self):
    #     """
    #     Work required from the flow.
    #     """
    #     w_required = 0
    #     for c in self.components:
    #         if c.__class__.__name__ == 'turbine':
    #             w_required -= c.w_r()
    #     return w_required
    #
    # def E_balance(self):
    #     """
    #     Flow energy balance.
    #     """
    #     return self.Q_in() - self.W_req()
    #
    # def E_prop(self):
    #     """
    #     Energy added to the flow for propulsion.
    #     """
    #     return self.v_exit()**2/2
    #
    # def prop_efficiency(self):
    #     """
    #     Stream propulsive efficiency.
    #     """
    #     return self.E_prop()/self.Q_in()

    def _plot_T_p(self,
                  show=False,
                  plot_label=None,
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
                              plot_label=plot_label,
                              show=show,
                              # Further customization
                              x_tick_ndecimals=2,
                              **further_custom)

    def _plot_p_V(self,
                  show=False,
                  plot_label=None,
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

        self.plot_cycle_graph(self.V(), self.p0()/1000,
                              color=color,
                              plot_label=plot_label,
                              show=show,
                              # Further customization
                              y_tick_ndecimals=2,
                              **further_custom)

    def _plot_T_S(self,                              # TODO: implement
                  show=False,
                  plot_label=None,
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
                         plot_label,
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
                # Figure
                fig=fig,
                # Further customization
                plot_label=plot_label,
                x_label=x_label,
                y_label=y_label,
                show=show,
                **further_custom)

    """
    System takeover and API functions
    """
    def _system_takeover(self, method, **kwargs):
        if hasattr(self, 'system'):
            getattr(self.system, method)(**kwargs)
        else:
            getattr(self, '_' + method)(**kwargs)

    def run(self, log=True):
        args = locals()
        del args['self']

        self._system_takeover('run', **args)

    def fmf(self):
        """
        Stream fuel mass flow
        """
        self._system_takeover('fmf')

    def thrust(self):
        """
        Flow thrust
        """
        self._system_takeover('thrust')

    def sfc(self):
        """
        Specific fuel consumption
        """
        self._system_takeover('sfc')

    # def Q_in(self):               #TODO: verify and implement efficiency calculations
    #     """
    #     Heat provided to the flow.
    #     """
    #     q_provided = 0
    #     for c in self.components:
    #         if c.__class__.__name__ == 'combustion_chamber':
    #             q_provided += c.Q
    #     return q_provided
    #
    # def W_req(self):
    #     """
    #     Work required from the flow.
    #     """
    #     w_required = 0
    #     for c in self.components:
    #         if c.__class__.__name__ == 'turbine':
    #             w_required -= c.w_r()
    #     return w_required
    #
    # def E_balance(self):
    #     """
    #     Flow energy balance.
    #     """
    #     return self.Q_in() - self.W_req()
    #
    # def E_prop(self):
    #     """
    #     Energy added to the flow for propulsion.
    #     """
    #     return self.v_exit()**2/2
    #
    # def prop_efficiency(self):
    #     """
    #     Stream propulsive efficiency.
    #     """
    #     return self.E_prop()/self.Q_in()

    def plot_T_p(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._system_takeover('plot_T_p', **{**args, **kwargs})

    def plot_p_V(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._system_takeover('plot_p_V', **{**args, **kwargs})

    def plot_T_S(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._system_takeover('plot_T_S', **{**args, **kwargs})


class system:
    """
    System
    ------
    """
    def __init__(self, *args):
        """
        Create a system from two objects.

        :type args: stream
        """
        self.streams = []
        self._gobble(args)

    """
    Operators
    """
    def __call__(self, *args):
        """
        System stream addition operator: <system>(<list of streams>)

        :type args: stream
        """
        self._gobble(args)

    def _gobble(self, streams):
        """
        :type streams: list of stream
        """
        for s in streams:
            self.streams.append(s)
            s.system = self

    def __add__(self, other):
        """
        System addition operator: <system> + <stream/system>

        :type other: system
        """
        streams = list(set(self.streams) & set(other.streams))
        return system(*streams)

    """
    System functions
    """
    def run(self, log=True):
        """
        Run stream system.
        """

        self._sort_streams()

        n = 0
        while not all([s.ran for s in self.streams]):
            for s in self.streams:
                if s.stream_id[0] == n:
                    s._run(log)
            n += 1

    def _sort_streams(self):
        """
        Sort system streams based on their stream ID
        """
        ids     = [''.join(str(c) for c in stream.stream_id) for stream in self.streams]
        indexes = [float(id.replace('m', '.1').replace('s', '.2')) for id in ids]
        self.streams = [s for _, s in sorted(zip(indexes, self.streams))]

    def fmf(self):
        pass

    def thrust(self):
        pass

    def sfc(self):
        pass

    def _plot(self,
              x, y,
              x_scale=1, y_scale=1,
              x_label=None, y_label=None,
              show=False,
              plot_label=None,                  # When called from a _system_takeover the plot_label and color
              color=colorscheme_one()[0],       # arguments are passed to the function, but disregarded.
              **kwargs):
        """
        System plot
        -----------

        x and y are the stream parameters to be
        plotted for each stream.

        Process
        1. Create figure
        2. Create state variable and plotters vectors
            2.1 Parent connectors
        3. comparison call

        comparison call
            - fig=None, ax=None -> plot_cycle_graph -> fig in **kwargs keys
                - fig=None, ax=None -> line, scatter
                    - line, scatter plot onto active figure, axis

        :param x_scale: Scaling factor.
        :param y_scale: Scaling factor.

        :type x:        str
        :type y:        str
        :type x_scale:  float
        :type y_scale:  float
        """
        plotters   = []
        x_system   = []
        y_system   = []

        # 1. Create figure
        figure((9, 5))

        # 2. Create state variable and plotters vectors
        for stream in self.streams:

            # Plot defaults
            defaults = {'plot_label': f'{".".join([str(c) for c in stream.stream_id])}',
                        'x_label': x_label,
                        'y_label': y_label,
                        'color': colorscheme_one()[self.streams.index(stream)],
                        'zorder': 10-self.streams.index(stream)
                        }

            def gen_plotter(**defaults):
                """
                Returns a plotter using the defaults.
                Any keyword arguemnts passed to the
                _plot function overwrite the defaults.
                """
                return lambda x, y, **kwargs: stream.plot_cycle_graph(x=x, y=y, **{**kwargs, **defaults})

            x_stream = getattr(stream, x)()/x_scale
            y_stream = getattr(stream, y)()/y_scale

            plotters.append(gen_plotter(**defaults))
            x_system.append(x_stream)
            y_system.append(y_stream)

            # 2.1 Parent connectors
            if hasattr(stream, 'parents'):
                for parent in stream.parents:
                    x_parent = getattr(parent, x)()/x_scale
                    y_parent = getattr(parent, y)()/y_scale
                    # If the parent stream has no stages, get parent stream's gas state
                    p_x = x_parent[-1] if len(x_parent) != 0 else getattr(parent.gas, x)/x_scale
                    p_y = y_parent[-1] if len(y_parent) != 0 else getattr(parent.gas, y)/y_scale
                    if len(stream.components) > 0:
                        x_system.append(np.array([p_x, x_stream[0]]))
                        y_system.append(np.array([p_y, y_stream[0]]))
                        plotters.append(gen_plotter(color=defaults['color'], x_label=None, y_label=None))

        # 2.2 Remove streams with no stages
        mask_x = np.array([a.size != 0 for a in x_system])
        mask_y = np.array([a.size != 0 for a in y_system])
        mask = mask_x * mask_y  # Ensure that any x-y array pairs with an empty array are removed

        x_system = np.array(x_system, dtype='object')[mask].tolist()
        y_system = np.array(y_system, dtype='object')[mask].tolist()
        plotters = np.array(plotters, dtype='object')[mask].tolist()

        # 4. comparison call
        #     - fig=None, ax=None -> plot_cycle_graph -> fig in **kwargs keys
        #         - fig=None, ax=None -> line, scatter
        #             - line, scatter plot onto active figure, axis
        comparison(x=x_system, y=y_system, f=plotters,
                   legend_loc=(0.875, 0.4),
                   show=show,
                   **kwargs)

    def plot_T_p(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs
                 ):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._plot(x='p0', x_scale=1/1000, x_label='p$_0$ [kPa]',
                   y='t0', y_scale=1,      y_label='T$_0$ [K]',
                   **{**args, **kwargs})

    def plot_p_V(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):                             # TODO: implement diagram integrating all streams
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._plot(x='V',                  x_label='v$_0$ [m$^3$/n]',
                   y='p0', y_scale=1/1000, y_label='p$_0$ [kPa]',
                   **{**args, **kwargs})

    def plot_T_S(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):                             # TODO: implement diagram integrating all streams
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self._plot(x='S',  x_label='S [J/K]',
                   y='t0', y_label='T$_0$ [K]',
                   **{**args, **kwargs})
