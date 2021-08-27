import re


class shaft:
    """
    Shaft class
    """
    def __init__(self, *args):
        for component in args:
            component.shaft = self
            setattr(self, self._comp_name(component), component)
            print(self.__dict__.keys())

    def components(self):
        return [v for v, k in self.__dict__.keys() if re.match(r'[s, p]\d{1,3}', k)]

    def component_names(self):
        return [k for v, k in self.__dict__.keys() if re.match(r'[s, p]\d{1,3}', k)]

    def component_classes(self):
        return [c.component.__class__.__name__ for c in self.components()]

    def _comp_name(self, comp):
        """
        Return the component name for a given
        component of a cycle instance to
        ease retrieving components.
        """
        comp_class = comp.__class__.__name__
        keys       = [k for k in self.__dict__.keys()]
        name       = comp_class

        n = 0   # Number of components of the same class
        while name in keys:
            if name[-1].isnumeric:
                name = name[:-1]
            name = name + (str(n) if n > 0 else '')
            n += 1

        if n == 1:
            comp0 = comp_class + '1'
            self.__dict__[comp0] = self.__dict__.pop(comp_class)
            return name
        else:
            return name

    def _count_instances(self, items):
        """
        :type items: list
        """
        n = 0  # Number of components of the same class
        for i in range(len(self.component_names())):            # as the input component in the cycle.
            if self.component_names()[i] in items:
                n += 1
            else:
                pass
        return n


class diversion:
    pass


if __name__ == '__main__':
    from src.components import compressor, turbine

    c1 = compressor(0.95, 2)
    t2 = turbine(0.9)

    s = shaft(c1, c1, t2)
