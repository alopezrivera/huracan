from termcolor import colored


def units(s, u):
    if not isinstance(s, type(str)):
        s = str(s)
    return s + ' '*(35-len(s.replace("\n", ""))) + '[{}]'.format(u.rstrip())


def result(var, val, u, r=4):
    print(units(str('{} = {:,.'+'{}'.format(r)+'f}').format(var, val), u))


def print_p_t(p, t, stage='n+1'):
    result('p0_{}'.format(stage), p, 'Pa')
    result('T0_{}'.format(stage), t, 'K')


def print_color(text, color):
    print(colored(text, color))


def print_positive(text):
    print(colored(text, 'yellow'))


def print_negative(text):
    print(colored(text, 'yellow'))


def cycle_graph(x, y, title):
    import matplotlib.pyplot as plt
    from mpl_plotter.two_d import line, scatter

    line(x=x, y=y, color='grey', line_width=1, zorder=1, alpha=0.65)
    scatter(ax=plt.gca(), fig=plt.gcf(), x=x, y=y, norm=y,
            point_size=100, zorder=2, cmap='RdYlBu_r',
            x_tick_number=5, y_tick_number=5, title=title,
            x_label='p', y_label='T [K]', y_label_rotation=90, show=True)


def out(arg):
    import sys
    print_color(arg, 'red')
    sys.exit()
