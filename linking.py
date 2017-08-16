from collections import defaultdict
from formula import Bot, Top

class Linking(object):
    """
    Represents a linking for a formula of MLL
    """
    def __init__(self, formula, links):
        """
        :param formula: the formula that the linking is about
        :param links: a list of pairs of indices representing the linking
        """
        super(Linking, self).__init__()
        self.formula = formula
        self.links = links
        self.forward = {a:b for a,b in links}
        self.backward = defaultdict(list)
        for a, b in links:
            self.backward[b].append(a)
        for b in self.backward:
            cur_list = self.backward[b]
            smaller = [a for a in cur_list if a < b]
            greater = [a for a in cur_list if b < a]
            self.backward[b] = sorted(smaller) + sorted(greater, reverse=True)

    def syntactically_valid(self, strict=True):
        """
        Makes sure the linking is syntactically valid: it goes from bottoms
        to subformulae not containing these units. If strict=True,
        enforces that they link to tops.
        """
        all_links_are_valid = all(
            self.valid_link(start, end, strict=strict)
            for start, end in self.links
        )
        all_bots_are_covered = all(
            idx in self.forward
            for idx, subformula in enumerate(self.formula)
            if isinstance(subformula, Bot)
        )
        return all_links_are_valid and all_bots_are_covered

    def valid_link(self, start, end, strict=True):
        """
        Same as syntactically_valid but for a single link
        """
        start_formula = self.formula[start]
        end_formula = self.formula[end]

        if not isinstance(start_formula, Bot):
            return False

        if strict:
            return isinstance(end_formula, Top)
        else:
            return end < start or end >= start + len(start_formula)

    def stack_condition(self):
        stack = []

        raise NotImplementedError()

    def is_symmetric_proof(self):
        from switching import Switching
        return all(
            switch.acyclic_and_connected()
            for switch in Switching.enumerate(self)
        )

    @classmethod
    def enumerate(cls, formula):
        """
        Generates all the valid linkings for a formula
        """
        bot_indices = list(
            idx
            for idx, subformula in enumerate(formula)
            if isinstance(subformula, Bot)
        )

        top_indices = list(
            idx
            for idx, subformula in enumerate(formula)
            if isinstance(subformula, Top)
        )

        # Generate the exponential of the set
        l = len(bot_indices)
        k = len(top_indices)
        bound = pow(k,l)
        for i in range(bound):
            remainder = i
            dct = {}
            for j in range(l):
                dct[bot_indices[j]] = top_indices[remainder % k]
                remainder = remainder // k
            yield cls(formula, list(dct.items()))

    @classmethod
    def enumerate_symmetric_proofs(cls, formula):
        return (
            linking
            for linking in cls.enumerate(formula)
            if linking.is_symmetric_proof()
        )

