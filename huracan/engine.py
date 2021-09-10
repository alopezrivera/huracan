# SPDX-FileCopyrightText: © 2021 Antonio López Rivera <antonlopezr99@gmail.com>
# SPDX-License-Identifier: MPL-2.0

"""
Huracan engine elements
-----------------------
"""

import re
import types
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
        self.runtime_d = {}
        if not isinstance(fr, type(None)):
            self.runtime_d['fr'] = fr

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
            self.add_component(other)
            return self
        if isinstance(other, stream):               # TODO: stream merge
            return self.add_stream(other)

    def add_component(self, c):
        """
        Component addition
        """
        self.components.append(c)
        c.downstream = self.downstream
        c.stream = self

    def add_stream(self, s):
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
        return self.divert(other)

    def divert(self, fr, names=None):
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
            mf_matrix = mf_matrix[mf_matrix[:, 0].argsort()]

            for i in range(mf_matrix[:, 1].size):
                sub_id = 'm' if i == 0 else f's{i}' if i > 1 else 's'
                mf_matrix[i, 1].stream_id.append(sub_id)

        if hasattr(self, 'system'):
            self.system(main, div)
            main.system = div.system = self.system
        else:
            system(self, main, div)

        return main, div

    def __getitem__(self, item):
        """
        Component retrieval operator: <stream>[<component stage name>]
        """
        return self.retrieve(item)

    def retrieve(self, item):
        """
        Retrieve any stream component by its stage name.

        :type item: str
        """
        assert item in self.stages(), 'Specified a non-existent stage.'

        for c in self.components:
            if c.stage == item:
                return c

    """
    Utilities
    """
    def stages(self):
        """
        Return a list containing the stage name of each
        component in the stream.
        """
        return [c.stage for c in self.components]

    def stage_name(self, c):
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
                 'nozzle':             'nz',

                 'intercooler':        'ic',
                 'recuperator':        'rc',
                 'afterburner':        'ab',
                 }

        code = codes[c.__class__.__name__] + self.n_instances(c)

        return f'{".".join([str(c) for c in self.stream_id])}.{code}'

    def n_instances(self, comp):
        """
        Calculate the number of instances of a given component's
        parent class in the stream (n), and its index in the
        stream's components list (i).

        The index of the component is returned as follows:
        - If the given component is the only instance of its parent
          class in the stream (n = 1):
            - ''                                     (empty string)
        - If the given component is one of more instances of its
          parent class in the stream (n > 1):
            - str(i + 1)                    (numeral starting at 1)

        :type comp: component
        """

        i = 0       # Component index
        n = 0       # Number of instances of the input component's class in the stream
        for c in self.components:
            if comp is c:
                i = n
            if comp.__class__.__name__ == c.__class__.__name__:
                n += 1

        return '' if n == 1 else str(i + 1)

    def log(self):

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
    Stream runtime functions
    """
    def run(self, log=True):
        """
        Execute the transfer functions of all components in the stream
        on the instance's gas class instance.
        """

        self.runtime()

        assert hasattr(self, 'gas'), 'stream does not have a gas attribute.'

        self.choked = False                                 # FIXME: choked flow implementation is ugly

        for c in self.components:
            c(self.gas)                     # Run thermodynamic process on stream gas
            c.stage = self.stage_name(c)   # Set component stage name

            if hasattr(c, 'choked') and c.choked:           # FIXME: ugly
                self.choked = c.choked

        # Indicate stream has been run.
        self.ran = True

        if log:
            self.log()

    def runtime(self):
        if hasattr(self, 'parents') and len(self.parents) > 1:
            self.merge()

        for k, v in self.runtime_d.items():
            f = getattr(self, k)
            f(v)

    def merge(self):
        if hasattr(self, 'gas'):
            for s in self.parents:
                self.gas += s.gas
        else:
            self.gas = self.parents[0].gas
            for s in self.parents[1:]:
                self.gas += s.gas

    def fr(self, fr):
        self.gas, _ = fr * deepcopy(self.gas)

    """
    Stream fluid state
    """
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

    def S(self):
        """
        Specific entropy vector.
        """
        assert self.ran, 'The stream must be run to obtain the specific entropy at each stage'

        return np.array([c.S for c in self.components])

    def H(self):
        """
        Specific enthalpy vector.
        """
        assert self.ran, 'The stream must be run to obtain the specific entropy at each stage'

        return np.array([c.H for c in self.components])

    """
    System takeover
    """
    def system_takeover(self):
        """
        System takeover
        ---------------

        When a stream is integrated in a system, all
        stream methods with a homonimous system method
        are renamed as protected stream instance attributes,
        and new "takeover" methods take their name.
        """

        special = r'^__(.*?)\__$'

        def takeover(obj, method):
            if hasattr(obj.system, method):
                return getattr(obj.system, method)
            else:
                return getattr(obj, '_' + method)

        for k in dir(self):
            v = getattr(self, k)
            print('A')
            print(k, type(v), isinstance(v, types.MethodType))
            # If the attribute k is:
            #    - a method
            #    - which is not special
            #    - whose name is the name of another method in the stream's sytem
            if isinstance(v, types.MethodType) and not re.match(special, k) and k in dir(self.system):
                setattr(self, '_' + k, v)

                print(getattr(self, '_' + k))

                setattr(self, k, takeover(self, k))

    """
    Stream outlet flow characteristics
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
        # Absolute temperature before the stream exit (likely but not necessarily a nozzle)
        if len(self.components) > 1:
            # If the stream has more components than 1, the absolute temperature
            # after the component previous to the last one is taken.
            if self.components[-1].__class__.__name__ == 'nozzle':
                t_before_exit = self.components[-2].t0
            else:
                t_before_exit = self.components[-1].t0
        else:
            if hasattr(self, 'parents'):
                # If the stream has a single component and a parent stream or streams
                if len(self.parents) > 1:
                    # If the stream has more than a single parent stream, the gases
                    # of each parent are copied, merged and the absolute temperature
                    # of the resulting gas mixture is taken.
                    for i in range(len(self.parents)):
                        if i == 0:
                            g = deepcopy(self.parents[i].gas)
                        else:
                            g += deepcopy(self.parents[i].gas)
                    t_before_exit = g.t0
                else:
                    # If the stream has a single parent, the absolute temperature
                    # of the parent's gas is taken.
                    t_before_exit = self.parents[0].gas.t0
            else:
                # Is the stream has a single component and no parent streams,
                # it is assumed that the setup consists of a intake-nozzle
                # setup, and the absolute temperature of the moving gas is
                # taken.
                t_before_exit = deepcopy(self.gas).absolute().t01

        if self.choked:
            return (self.gas.k(t_before_exit)*R*t_before_exit)**0.5         # M=1 immediately before nozzle exit
        else:
            assert t_before_exit - self.gas.t0 > 0, 'The total temperature of the flow is lower before ' \
                                                    'the nozzle tha outside the engine: this happens due to the ' \
                                                    'compressors not providing enough energy to the flow. You must ' \
                                                    'either increase the pressure ratio of the compressors or ' \
                                                    'decrease the power extracted from the flow to solve the ' \
                                                    'inconsistency.'
            return (2*self.gas.cp(t_before_exit)*(t_before_exit - self.gas.t0))**0.5    # Heat -> Kinetic energy

    def A_exit(self):
        """
        Nozzle exit area
        """
        return self.gas.mf*R*self.gas.t0/(self.gas.p0*self._v_exit())

    """
    Stream performance analysis
    """
    def fmf(self):
        """
        Stream fuel mass flow
        """
        fmf = 0
        for c in self.components:
            if hasattr(c, 'fuel') and hasattr(c.fuel, 'mf'):
                fmf += c.fuel.mf
        return fmf

    def flow_thrust(self):
        """
        Flow thrust

        If the flow is choked, the expansion of the gas contributes to the thrust of the flow.
        """
        if self.choked:
            return self.gas.mf * (self._v_exit() - self.gas.v_0) + self._A_exit() * (
                        self.gas.p0 - self.gas.p_0)
        else:
            return self.gas.mf * (self._v_exit() - self.gas.v_0)

    def prop_thrust(self):
        """
        Propeller/propfan thrust
        """
        if any([c.__class__.__name__ in ['prop', 'propfan'] for c in self.components]):
            propellers = [c for c in self.components if c.__class__.__name__ in ['prop', 'propfan']]
            prop_thrust = sum([prop.thrust(self.gas.v_0) for prop in propellers])
        else:
            prop_thrust = 0
        return prop_thrust

    def total_thrust(self):
        """
        Flow thrust plus propeller/propfan thrust
        """
        return self._flow_thrust() + self._prop_thrust()

    def sfc(self):
        """
        Specific fuel consumption
        """
        return self.fmf()/self.flow_thrust()

    def Q_in(self):                #TODO: verify efficiency calculations
        """
        Heat provided to the flow.
        """
        q_provided = 0
        for c in self.components:
            if c.__class__.__name__ == 'combustion_chamber':
                q_provided += c.Q
        return q_provided

    def W_req(self):
        """
        Work required from the flow.
        """
        w_required = 0
        for c in self.components:
            if c.__class__.__name__ in ['fan',
                                        'prop',
                                        'propfan',
                                        'compressor']:
                w_required += c.w
        return w_required

    def E_balance(self):
        """
        Flow energy balance.
        """
        return self._Q_in() - self._W_req()

    def E_prop(self):
        """
        Energy added to the flow for propulsion.
        """
        return self._v_exit()**2/2

    def efficiency(self):
        """
        Engine efficiency
        """
        return self._E_balance()/self._Q_in()

    def prop_efficiency(self):
        """
        Stream propulsive efficiency.
        """
        return self._E_prop()/self._Q_in()

    """
    Plots
    """
    def plot_T_p(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Total pressure
        - Total temperature
        """

        figure((9, 5))

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

    def plot_p_V(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Total specific volume
        - Total pressure
        """

        figure((9, 5))

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

    def plot_T_S(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Specific entropy
        - Total temperature
        """

        figure((9, 5))

        defaults = {'x_label': 'S [J/K/n]',
                    'y_label': 'T$_0$ [K]',}

        further_custom = {**defaults, **kwargs}

        self.plot_cycle_graph(self.S(), self.t0() / 1000,
                              color=color,
                              plot_label=plot_label,
                              show=show,
                              # Further customization
                              y_tick_ndecimals=2,
                              **further_custom)

    def plot_p_H(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        """
        Plot
        - Specific entropy
        - Total temperature
        """

        figure((9, 5))

        defaults = {'x_label': 'p$_0$ [kPa]',
                    'y_label': 'H$_0$ [J]',}

        further_custom = {**defaults, **kwargs}

        self.plot_cycle_graph(self.p0(), self.H() / 1000,
                              color=color,
                              plot_label=plot_label,
                              show=show,
                              # Further customization
                              y_tick_ndecimals=2,
                              **further_custom)

    def plot_cycle_graph(self,
                         x, y,
                         plot_label,
                         x_label, y_label,
                         color=colorscheme_one()[0],
                         show=False,
                         **kwargs
                         ):
        """
        General plot composed of an MPL Plotter line and scatter plot.

        The default arguments plus any valid MPL Plotter line plotting
        class arguments can be passed to this function.
        """
        fig = kwargs.pop('fig', None)

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
            'y_label_pad': 5,
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
        self.gobble(list(args))

    """
    Operators
    """
    def __call__(self, *args):
        """
        System stream addition operator: <system>(<list of streams>)

        :type args: stream
        """
        self.gobble(list(args))

    def gobble(self, streams):
        """
        :type streams: list of stream
        """
        for s in streams:
            self.streams.append(s)
            s.system = self
            s.system_takeover()

    def __add__(self, other):
        """
        System addition operator: <system> + <stream/system>

        :type other: system
        """
        streams = list(set(self.streams) & set(other.streams))
        return system(*streams)

    def __getitem__(self, item):
        """
        Component retrieval operator: <system>[<component stage name>]
        """
        return self.retrieve(item)

    def retrieve(self, item):
        """
        Retrieve any stream component by its stage name.

        :type item: str
        """
        components = []
        for s in self.streams:
            components += s.components

        assert item in [c.stage for c in components], 'Specified a non-existent stage.'

        for c in components:
            if c.stage == item:
                return c

    """
    System functions
    """
    def run(self, log=True):
        """
        Run stream system.
        """

        self.sort_streams()

        n = 0
        while not all([s.ran for s in self.streams]):
            for s in self.streams:
                if s.stream_id[0] == n:
                    s._run(log)
            n += 1

    def sort_streams(self):
        """
        Sort system streams based on their stream ID
        """
        ids     = [''.join(str(c) for c in stream.stream_id) for stream in self.streams]
        indexes = [float(id.replace('m', '.1').replace('s', '.2')) for id in ids]
        self.streams = [s for _, s in sorted(zip(indexes, self.streams))]

    def parents(self):
        """
        Return all system streams with children.
        Useful to not calculate thrust, exit velocity
        and other stream outlet values for streams
        flowing to children streams.
        """
        parents = []
        for s in self.streams:
            parents += s.parents if hasattr(s, 'parents') else []
        return parents

    """
    Stream outlet flow characteristics
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
        v = [s._v_exit() for s in self.streams if s not in self.parents()]
        return v[0] if len(v) == 1 else v

    def A_exit(self):
        """
        Nozzle exit area
        """
        a = [s._A_exit() for s in self.streams if 'nozzle' in [c.__class__.__name__ for c in s.components]]
        return a[0] if len(a) == 1 else a

    """
    System performance analysis
    """
    def fmf(self):
        return sum([s._fmf() for s in self.streams])

    def flow_thrust(self):
        return sum([s._flow_thrust() for s in self.streams if s not in self.parents()])

    def prop_thrust(self):
        return sum([s._prop_thrust() for s in self.streams])

    def total_thrust(self):
        return self.flow_thrust() + self.prop_thrust()

    def sfc(self):
        return self.fmf()/self.flow_thrust()

    def Q_in(self):                 # TODO: verify efficiency calculations
        """
        Heat provided to the flow.
        """
        return sum([s.Q_in() for s in self.streams])

    def W_req(self):
        """
        Work required from the flow.
        """
        return sum([s.W_req() for s in self.streams])

    def E_balance(self):
        """
        Flow energy balance.
        """
        return self.Q_in() - self.W_req()

    def E_prop(self):
        """
        Energy added to the flow for propulsion.
        """
        return sum([s.E_prop() for s in self.streams])

    def efficiency(self):
        """
        System efficiency
        """
        return self.E_balance()/self.Q_in()

    def prop_efficiency(self):
        """
        Stream propulsive efficiency.
        """
        return self.E_prop()/self.Q_in()

    """
    Plots
    """
    def plot(self,
             x, y,
             x_scale=None, y_scale=None,
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

        scales     = {'t0': 1,
                      'p0': 1/1000,
                      'V':  1,
                      'S':  1,
                      'H':  1}
        x_scale    = scales[x] if isinstance(x_scale, type(None)) else x_scale
        y_scale    = scales[y] if isinstance(y_scale, type(None)) else y_scale

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

            x_stream = getattr(stream, x)()*x_scale
            y_stream = getattr(stream, y)()*y_scale

            plotters.append(gen_plotter(**defaults))
            x_system.append(x_stream)
            y_system.append(y_stream)

            # 2.1 Parent connectors
            if hasattr(stream, 'parents'):
                for parent in stream.parents:
                    x_parent = getattr(parent, x)()*x_scale
                    y_parent = getattr(parent, y)()*y_scale
                    # If the parent stream has no stages, get parent stream's gas state
                    p_x = x_parent[-1] if len(x_parent) != 0 else getattr(parent.gas, x)*x_scale
                    p_y = y_parent[-1] if len(y_parent) != 0 else getattr(parent.gas, y)*y_scale
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
                   legend_loc=(0.875, 0.425),
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

        self.plot(x='p0', x_label='p$_0$ [kPa]',
                  y='t0', y_label='T$_0$ [K]',
                  **{**args, **kwargs})

    def plot_p_V(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self.plot(x='V',  x_label='v$_0$ [m$^3$/n]',
                  y='p0', y_label='p$_0$ [kPa]',
                  **{**args, **kwargs})

    def plot_T_S(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self.plot(x='S',  x_label='S [J/K]',
                  y='t0', y_label='T$_0$ [K]',
                  **{**args, **kwargs})

    def plot_p_H(self,
                 show=False,
                 plot_label=None,
                 color=colorscheme_one()[0],
                 **kwargs):
        args = locals()
        args.pop('self', None)
        args.pop('kwargs', None)

        self.plot(x='p0',  x_label='p$_0$ [kPa]',
                  y='H', y_label='H$_0$ [J]',
                  **{**args, **kwargs})
