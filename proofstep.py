from rbgraph import R, B, r, b

class ProofStep(object):
    def __init__(self, terms, position):
        self.terms = terms
        self.position = position

    def commutes_with_previous(self, proofstep, parent_terms):
        """
        Given the previous proof step "proofstep",
        can we commute the two?

        If so, returns the commuted proof sequence
        as a two-element list.
        """
        raise NotImplemented

    def number_of_premises(self):
        """
        Number of premises of this logical rule
        """
        raise NotImplemented

class UnitAxiom(ProofStep):
    def __repr__(self):
        return "unit"

    def commutes_with_previous(self, proofstep, parent_terms):
        pp = proofstep.position
        secondstep = proofstep.copy()
        secondstep.terms = self.terms
        if self.position <= pp:
            firststep_offset = 0
            secondstep.position += 1
        else:
            firststep_offset = proofstep.number_of_premises()-1
            
        p = self.position + firststep_offset
        firststep = UnitAxiom(parent_terms[:p] + [B(r)] + parent_terms[p:],
                        self.position)
        yield [firststep, secondstep]

    def number_of_premises(self):
        return 0

    @classmethod
    def from_parent(cls, terms, position):
        return UnitAxiom(terms[:position] + [B(r)] + terms[position:], position)

    def copy(self):
        return UnitAxiom(self.terms, self.position)


class MergeStep(ProofStep):
    def __init__(self, terms, position, coords):
        super(MergeStep, self).__init__(terms, position)
        self.coords = coords

    def __repr__(self):
        return "merge {} at {}".format(self.position, self.coords)

    def commutes_with_previous(self, proofstep, parent_terms):
        pp = proofstep.position
        secondstep = proofstep.copy()
        secondstep.terms = self.terms
        if pp.position < self.position:
            # This is a simple exchange
            firststep_pos = self.position + proofstep.number_of_premises()-1
            lhs = parent_terms[firststep_pos]
            rhs = parent_terms[firststep_pos+1]
            firststep = MergeStep(parent_terms[:firststep_pos] + [lhs.merge(rhs,self.coords)] +
                                  parent_terms[firststep_pos+2:], firststep_pos, self.coords)
            yield [firststep, secondstep]
        elif pp.position > self.position+1:
            # This is also a simple exchange
            lhs = parent_terms[self.position]
            rhs = parent_terms[self.position+1]
            firststep = MergeStep(parent_terms[:self.position] + [lhs.merge(rhs,self.coords)] +
                                  parent_terms[self.position+2:], self.position, self.coords)
            secondstep.position += 1
            yield [firststep, secondstep]
        else:
            # Here comes the tricky part

            # We cannot permute overlapping UnitAxioms and MergeSteps
            # because we have assumed that all the merges are nontrivial
            if isinstance(proofstep, UnitAxiom):
                return

            # If we have two merges to commute, we just look for an alternative path
            p_first_merge = self.position+1 if self.position == pp else self.position
            p_third_term = self.position if self.position == pp else self.position+2
            a = parent_terms[p_third_term]
            b = parent_terms[p_first_merge]
            c = parent_terms[p_first_merge+1]
            target = self.terms[self.position]
            for term,i1,j1,k1,l1 in possible_merges(b, c):
                if self.position == pp:
                    second_merges = possible_merges(a, term)
                else:
                    second_merges = possiblel_merges(term, a)
                for candidate,i2,j2,k2,l2 in second_merges:
                    if candidate == target:
                        firststep = MergeStep(parent_terms[:p_first_merge] + [term] +
                                              parent_terms[p_first_merge+1:], p_first_merge,
                                              (i1,j1,k1,l1))
                        secondstep = MergeStep(self.terms, self.position, (i2,j2,k2,l2))
                        yield [firststep, secondstep]

    def number_of_premises(self):
        return 2

    @classmethod
    def from_parent(cls, terms, position, coords):
        i,j,k,l = coords
        return MergeStep(terms[:position] + [terms[position].merge(terms[position+1], i,j,k,l)] + terms[position+2:],
                        position, coords)

    def copy(self):
        return MergeStep(self.terms, self.position, self.coords)

