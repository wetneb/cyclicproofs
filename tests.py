import unittest

from rbgraph import RBG as G

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


