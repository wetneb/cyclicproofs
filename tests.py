import unittest

from rbgraph import RBG, R, B, r, b
from proofstep import UnitAxiom, MergeStep
from proof import Proof

class RBGTest(unittest.TestCase):
    def test_simple_equality(self):
        self.assertEqual(B(), B())
        self.assertEqual(B(r), R(b))
        self.assertNotEqual(B(), B(r))
        self.assertNotEqual(B(r), B(r,r))
        self.assertEqual(B(r,r,R(b,b)), B(r,R(b,b),r))

    def test_merge(self):
        # creating a gadget
        unit = R(b)
        gadget = unit.merge(unit)
        self.assertEqual(B(r, R(b,b), r), gadget)
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

class ProofStepTest(unittest.TestCase):
    def test_commutes_with_previous_unit(self):
        parent = (B(r),B(r))
        firststep = MergeStep.from_parent(parent, 0, (0,0,0,0))
        secondstep = UnitAxiom.from_parent(firststep.terms, 1)
        commutation = list(secondstep.commutes_with_previous(firststep, parent))
        self.assertEqual(commutation,
            [(UnitAxiom((B(r),B(r),B(r)),2),MergeStep((B(r,R(b,b),r),B(r)), 0, (0,0,0,0)))])

    def test_commutes_with_previous_merge(self):
        parent = (B(r),B(r),B(r))
        firststep = MergeStep.from_parent(parent, 0, (0,0,0,0))
        secondstep = MergeStep.from_parent(firststep.terms, 0, (0,1,0,0))
        firststep2 = MergeStep.from_parent(parent, 1, (0,0,0,0))
        secondstep2 = MergeStep.from_parent(firststep2.terms, 0, (0,0,0,1))
        commutation = list(secondstep.commutes_with_previous(firststep, parent))
        self.assertEqual(commutation,
              [(firststep2, secondstep2)])

    def test_exchange_merges(self):
        parent = (B(r),B(r),B(r),B(r))
        firststep = MergeStep.from_parent(parent, 0, (0,0,0,0))
        secondstep = MergeStep.from_parent(firststep.terms, 1, (0,0,0,0))
        firststep2 = MergeStep.from_parent(parent, 2, (0,0,0,0))
        secondstep2 = MergeStep.from_parent(firststep2.terms, 0, (0,0,0,0))
        commutation = list(secondstep.commutes_with_previous(firststep, parent))
        self.assertEqual(commutation,
              [(firststep2, secondstep2)])
             
class ProofTest(unittest.TestCase):
    def test_neighbours(self):
        p1 = Proof().unit().unit()
        p2 = Proof().unit().unit(1)
        neighbours = list(p1.neighbours())
        self.assertEqual([p2], neighbours)

        pu = Proof().unit()
        self.assertEqual([], list(pu.neighbours()))

    def test_equivalence_class(self):
        p3 = Proof().unit().unit().unit().unit()
        p4 = p3.copy()
        self.assertEqual(len(list(p3.equivalence_class())), 24)
        # Of course this should still hold… but not if
        # equivalence_class makes nasty side effects under the hood!
        self.assertEqual(p3, p4)
        self.assertEqual(len(list(p3.equivalence_class())), 24)

    def test_proofs_with_two_merges(self):
        # proofs of depth 2 should all be equivalent
        backtrack = Proof.enumerate(2)
        proofs = list(Proof.reconstruct((), B(R(b,b),r,r,R(b,b),r), Proof(), backtrack))
        p0 = proofs[0]
        equiv_class = list(p0.equivalence_class())
        self.assertTrue(all(p in equiv_class for p in proofs))

    def test_unit_removal(self):
        p1 = Proof().unit().unit().unit()
        p1_no_units = p1.remove_unit_intros()
        self.assertEqual(len(p1_no_units), 0)
        self.assertEqual(p1.conclusion, p1_no_units.hypotheses)

        p2 = Proof().unit().unit().merge().unit().unit().merge(1)
        p2_no_units = p2.remove_unit_intros()
        self.assertEqual(len(p2_no_units), 2)
        self.assertEqual(p2.conclusion, p2_no_units.conclusion)

        # sliced proofs should still be hashable
        self.assertEqual(type(hash(p2_no_units)), int)

    def test_triple_unit(self):
        # the triple unit problem has two non-equivalent proofs
        backtrack = Proof.enumerate(3)
        proofs = list(Proof.reconstruct((), B(R(B(R(b,b),r),b),r,R(b,B(r,r))), Proof(), backtrack))
        self.assertEqual(len(proofs), 2)
        p0 = proofs[0]
        p1 = proofs[1]
        self.assertFalse(p0.equivalent(p1))

