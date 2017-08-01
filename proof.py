from hashable_collections.hashable_collections import hashable_list
from collections import defaultdict

from proofstep import UnitAxiom, MergeStep
from rbgraph import B, r

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

    def hypotheses_at_index(self, i):
        """
        Returns the hypotheses of the proof step at index idx
        """
        return self.steps[i-1].terms if i > 0 else self.hyp

    def remove_unit_intros(self):
        """
        Moves all the unit introductions to the top and returns
        the proof starting when all units have been introduced.
        """

        # First, lift all the units to the top, bubble-sort style
        merge_unit_found = True
        current_proof = self.copy()
        while merge_unit_found:
            merge_unit_found = False
            first_merge_index = len(self)
            for i in range(len(current_proof.steps)-1):
                a = current_proof.steps[i]
                b = current_proof.steps[i+1]
                if isinstance(a, MergeStep) and isinstance(b, UnitAxiom):
                    merge_unit_found = True
                    commutation = list(b.commutes_with_previous(a,
                            current_proof.hypotheses_at_index(i)))
                    newa, newb = commutation[0]
                    current_proof.steps[i] = newa
                    current_proof.steps[i+1] = newb

                # maintain the index of the first merge found
                if isinstance(a, MergeStep):
                    first_merge_index = min(first_merge_index, i)
                elif isinstance(b, MergeStep):
                    first_merge_index = min(first_merge_index, i+1)

        # Then, remove them
        new_hyp = current_proof.hypotheses_at_index(first_merge_index)
        current_proof.steps = hashable_list(current_proof.steps[first_merge_index:])
        current_proof.hyp = new_hyp
        return current_proof

    def neighbours(self):
        """
        Generates all the proofs that can be obtained with just one
        step of equivalence, starting from this proof.
        """
        for i in range(len(self)-1):
            first = self.steps[i]
            second = self.steps[i+1]
            parent = self.hypotheses_at_index(i)
            for commutation in second.commutes_with_previous(first, parent):
                [first,second] = commutation
                new_proof = self.copy()
                new_proof.steps[i] = first.copy()
                new_proof.steps[i+1] = second.copy()
                yield new_proof

    def equivalence_class(self, seen=None):
        """
        Returns a generator of the equivalence class
        of the current proof
        """
        if seen is None:
            seen = set()
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

    def equivalence_path(self, other, seen=None):
        """
        Generates ane equivalence path from the other
        to self
        """
        if seen is None:
            seen = set()
        seen.add(self)
        if other == self:
            return [self]
        for step in self.neighbours():
            if step in seen:
                continue
            path = step.equivalence_path(other, seen)
            if path:
                path.append(self)
                return path

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

    def __len__(self):
        return len(self.steps)

    def copy(self):
        new = Proof(self.hyp)
        new.steps = hashable_list(self.steps[:])
        return new

    def __hash__(self):
        return hash((self.hyp,self.steps))

    @classmethod
    def enumerate(cls, limit):
        """
        Enumerate all provable terms up to
        a certain proof depth
        """
        reachable = {}
        reachable[0] = {B(r):1}

        all_reachables = {B(r)}

        backtrack = defaultdict(list)
        # structure of this dict:
        # term -> list of (lhs,rhs,i,j,k,l)

        # fill each set of reacheable terms after m merges
        for m in range(1,limit+1):
            reachable[m] = {}
            # select a previous number of merges for the LHS
            for p in range(0,m):
                # loop through existing proofs for the LHS
                for lhs, num_lhs in reachable[p].items():
                    # loop through existing proofs for the RHS
                    for rhs, num_rhs in reachable[m-1-p].items():
                        # loop through possible merges
                        for term,i,j,k,l in lhs.possible_merges(rhs):
                            new_term = term not in all_reachables
                            if term in reachable[m]:
                                reachable[m][term] += num_lhs * num_rhs
                                backtrack[term]
                            elif new_term:
                                reachable[m][term] = num_lhs * num_rhs
                                all_reachables.add(term)

                            if term in reachable[m]:
                                backtrack[term].append(
                                    (lhs,rhs,i,j,k,l))

            #print('------{}------'.format(m))
            #for term, count in reachable[m].items():
            #    if term == triple_unit:
            #        print('triple unit:')
            #    print('{}\t{}'.format(count,term))
        return backtrack

    @classmethod
    def reconstruct(cls, left, term, proof_of_left, backtrack):
        """
        Prints all proofs of a given term, at the context [left, X, right]
        """
        if term == B(r):
            yield proof_of_left.unit(len(left))
        else:
            for lhs,rhs,i,j,k,l in backtrack[term]:
                proofs_of_lhs = cls.reconstruct(left, lhs, proof_of_left.copy(), backtrack)
                for proof_of_lhs in proofs_of_lhs:
                    proofs_of_lhs_rhs = cls.reconstruct(left+(lhs,), rhs, proof_of_lhs, backtrack)
                    for proof in proofs_of_lhs_rhs:
                        yield proof.merge(len(left), (i,j,k,l))


    def to_html(self):
        html = ''
        for j, step in enumerate(self.steps):
            name = 'img/{}'.format('-'.join(str(t) for t in step.terms))
            B.to_graphs(step.terms, 'output/'+name)
            html += '<p>{}</p>\n'.format(step)
            html += '<img src="{}.png" /><br />\n'.format(name)
        return html


