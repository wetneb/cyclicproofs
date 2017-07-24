import unittest

from rbgraph import RBG

G = RBG
R = RBG
B = RBG
r = R()
b = B()

class RBGTest(unittest.TestCase):
    def test_simple_equality(self):
        self.assertEqual(G(), G())
        g = G()
        self.assertEqual(G(g), G(g))
        self.assertNotEqual(G(), G(g))
        self.assertNotEqual(G(g), G(g,g))
        self.assertEqual(G(g,g,G(g,g)), G(g,G(g,g),g))

    def test_merge(self):
        # creating a gadget
        g = G()
        unit = G(g)
        gadget = unit.merge(unit)
        self.assertEqual(G(g, G(g,g), g), gadget)
        unit_again = unit.merge(unit, 0, 1, 0, 1)
        self.assertEqual(unit_again, unit)

    def test_red_simplification(self):
        unit = B(r)
        mixed = unit.merge(unit, 0, 1)
        self.assertEqual(mixed, unit)

    def test_units(self):
        unit = B(r)
        self.assertEqual(unit.units(), 1)
        gadget = unit.merge(unit)
        self.assertEqual(gadget.units(), 2)

    def test_triple_unit(self):
        unit = B(r)
        gadget = unit.merge(unit)
        # creating the triple unit with the identity strategy
        double_unit = unit.merge(gadget, 0, 0, 1, 2)
        self.assertEqual(double_unit, B(R(b,B(r,r)),R(b,b),r))
        # we are cyclic, not commutative, so equality fails here
        self.assertNotEqual(double_unit, B(R(B(r,r),b),R(b,b),r))
        triple_unit = double_unit.merge(unit, 1, 2)
        self.assertEqual(triple_unit,
            B(R(B(R(b,b),r),b),r,R(b,B(r,r))))

        # creating the triple unit with the non-identity strategy
        double_unit_2 = gadget.merge(unit, 0, 2)
        self.assertEqual(double_unit_2,
           B(R(B(R(b,b),r),b),r,r))
        triple_unit_2 = unit.merge(double_unit_2, 0, 0, 1, 2)
        self.assertEqual(triple_unit_2, triple_unit)

        # checking unit counts
        self.assertEqual(triple_unit.units(), 4)

    def test_order(self):
        unit = B(r)
        gadget = unit.merge(unit)
        weird1 = unit.merge(gadget, 0, 0, 0, 3)
        weird2 = unit.merge(gadget, 0, 0, 1, 3)
        self.assertNotEqual(weird1, weird2)
