from collections import defaultdict
from diskpartition import DiskPartition
from formula import Bot, Top, Tens, Parr

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

    def strongly_planar(self):
        disk = DiskPartition(self.links)
        return disk.is_planar()

    def is_symmetric_proof(self):
        from switching import Switching
        return all(
            switch.acyclic_and_connected()
            for switch in Switching.enumerate(self)
        )

    def is_neighbour(self, other):
        """
        Can this linking be rewired to the other in exactly one step?
        """
        common_links = set(self.links) & set(other.links)
        return len(common_links) == len(self.links) - 1

    def is_cyclic_proof(self):
        return self.strongly_planar() and self.is_symmetric_proof()

    @classmethod
    def enumerate(cls, formula):
        """
        Generates all the valid linkings for a formula
        """
        formula.cache_subformulae()
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

    @classmethod
    def enumerate_cyclic_proofs(cls, formula):
        return (
            linking
            for linking in cls.enumerate(formula)
            if linking.is_cyclic_proof()
        )

    @classmethod
    def graph_of_equivalences(cls, formula, fname):
        proofs = list(cls.enumerate_cyclic_proofs(formula))
        if len(proofs) <= 1:
            return (0, 0)

        # we do a union-find to keep track of the connected components
        parent = list(range(len(proofs)))
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def merge(i, j):
            pi = find(i)
            pj = find(j)
            parent[pi] = pj

        import graphviz as gv
        g = gv.Graph()
        for idx, p in enumerate(proofs):
            g.node(str(idx), label=str(idx))
            for idx2 in range(idx):
                q = proofs[idx2]
                if p.is_neighbour(q):
                    g.edge(str(idx), str(idx2))
                    merge(idx, idx2)
        # g.format = 'png'
        # g.render(filename='networks/'+fname)

        # count connected components
        cc = len(set(find(i) for i in range(len(proofs))))
        return (len(proofs), cc)

if __name__ == '__main__':

    import sys
    if len(sys.argv) <= 2:
        print('H&H')
        f = Parr(Top(), Parr(Tens(Bot(), Bot()), Parr(Top(), Parr(Tens(Bot(), Bot()), Top()))))
        for linking in Linking.enumerate_cyclic_proofs(f):
            print(linking.links)
        cc = Linking.graph_of_equivalences(f, 'hh')
        print(cc)
        print('triple unit')
        triple_unit = Parr(Parr(Tens(Parr(Tens(Bot(),Bot()),Top()),Bot()), Top()), Tens(Bot(), Parr(Top(), Top())))
        for linking in Linking.enumerate_cyclic_proofs(triple_unit):
            print(linking.links)
        cc = Linking.graph_of_equivalences(triple_unit, 'triple')
        print(cc)
        print('three proofs')
        gadget = Parr(Top(), Parr(Top(),Tens(Bot(), Bot())))
        three_proofs = Tens(gadget, gadget)
        for linking in Linking.enumerate_cyclic_proofs(three_proofs):
            print(linking.links)
        cc = Linking.graph_of_equivalences(three_proofs, 'three_proofs')
    else:
        start = int(sys.argv[1])
        end = int(sys.argv[2])

        for nb_nodes in range(start,end,2):
            print('all provable normalized formulae with {} nodes and more than one proof'.format(nb_nodes))
            for idx, formula in enumerate(Parr.enumerate_normalized(nb_nodes)):
                if (formula.valuation() == 1):
                    nb_proofs, cc = Linking.graph_of_equivalences(formula, 'enumerate-{}-{}'.format(nb_nodes, idx))
                    if cc:
                        print('{} {} {} ({})'.format(formula, nb_proofs, cc, idx))
