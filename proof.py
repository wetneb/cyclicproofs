from proofstep import UnitAxiom, MergeStep
from hashable_collections.hashable_collections import hashable_list

class Proof(object):
    """
    An object that represents a sequence
    of chained proof steps.
    """

    def __init__(self, hypotheses=()):
        """
        :param hypotheses: a list of graphs,
            representing the initial proof state.
        """
        self.hyp = hypotheses
        self.steps = hashable_list()

    @property
    def hypotheses(self):
        return self.hyp

    @property
    def conclusion(self):
        if self.steps:
            return self.steps[-1].terms
        return self.hyp

    def unit(self, position=0):
        """
        Introduce a unit at the given position.
        """
        self.add_step(UnitAxiom.from_parent(self.conclusion, position))
        return self

    def merge(self, position=0, coords=(0,0,0,0)):
        """
        Merge two adjacent graphs in the conclusion
        """
        self.add_step(MergeStep.from_parent(self.conclusion, position, coords))
        return self

    def add_step(self, step):
        """
        Add a proof step at the end of the current proof.
        """
        self.steps.append(step)

    def neighbours(self):
        """
        Generates all the proofs that can be obtained with just one
        step of equivalence, starting from this proof.
        """
        for i in range(len(self.steps)-1):
            first = self.steps[i]
            second = self.steps[i+1]
            parent = self.steps[i-1].terms if i > 0 else self.hyp
            for commutation in second.commutes_with_previous(first, parent):
                [first,second] = commutation
                new_proof = self.copy()
                new_proof.steps[i] = first
                new_proof.steps[i+1] = second
                yield new_proof

    def equivalence_class(self, seen=set()):
        """
        Returns a generator of the equivalence class
        of the current proof
        """
        seen.add(self)
        yield self
        for step in self.neighbours():
            if step in seen:
                continue
            yield from step.equivalence_class(seen=seen)

    def equivalent(self, other):
        """
        Returns a boolean: are these two proofs equivalent?
        """
        return other in self.equivalence_class()

    def __repr__(self):
        return (
                str(self.hyp) + '\n'+
                '\n'.join([
                    str(step) + '\n' + str(step.terms)
                    for step in self.steps])
                )

    def __eq__(self, other):
        return (self.hyp == other.hyp and
                self.steps == other.steps)

    def copy(self):
        new = Proof(self.hyp[:])
        new.steps = hashable_list(self.steps[:])
        return new

    def __hash__(self):
        return hash((self.hyp,self.steps))
