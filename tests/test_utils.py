import unittest

from huracan.utils import setattr_namespace


class TestsFluid(unittest.TestCase):

    def test_setattr_namespace(self):
        class a:
            pass

        print(type(a))

        b = a()

        c = 1

        setattr_namespace(b, locals())

