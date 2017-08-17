
class Formula(object):

    def to_string(self):
        raise NotImplementedError()

    @property
    def depth(self):
        raise NotImplementedError()

    @property
    def valuation(self):
        raise NotImplementedError()

    @property
    def normalized(self):
        raise NotImplementedError()

    def to_string_with_brackets(self):
        if self.depth:
            return "({})".format(self.to_string())
        else:
            return self.to_string()

    def walk(self):
        """
        Generates all the subformulae of this formula,
        in DFS order.
        """
        raise NotImplementedError()

    def __iter__(self):
        return self.walk()

    def __len__(self):
        return len(list(self.walk()))

    def __getitem__(self, idx):
        subf_cache = getattr(self, 'subformulae_cache', None)
        if subf_cache:
            return subf_cache[idx]
        for i, subformula in enumerate(self):
            if i == idx:
                return subformula
        raise ValueError("Index is out of bounds")

    def cache_subformulae(self):
        self.subformulae_cache = {
            i : f for i, f in enumerate(self)
        }

    def parent_map(self):
        """
        Returns a mapping of indexes to their parents
        """
        stack = []
        parent_map = {}
        for idx, subformula in enumerate(self):
            if stack:
                parent_map[idx] = stack[-1][1]

            stack.append(
                (subformula, idx, 0))

            pruning = True
            while pruning and stack:
                node, node_idx, nb_children = stack[-1]
                nb_expected_children = 2 if isinstance(node, BinaryFormula) else 0
                pruning = nb_expected_children == nb_children
                if pruning:
                    stack = stack[:-1]
                else:
                    stack[-1] = (node, node_idx, nb_children+1)
        return parent_map

    def __repr__(self):
        return self.to_string()

    @classmethod
    def enumerate(cls, nb_nodes):
        """
        Enumerates a sample of formulae with a given number of nodes
        """
        if not nb_nodes:
            return
        elif nb_nodes == 1:
            yield Bot()
            yield Top()
        else:
            for split in range(1,nb_nodes-1, 2):
                for a in cls.enumerate(split):
                    for b in cls.enumerate(nb_nodes - split - 1):
                        yield Parr(a, b)
                        yield Tens(a, b)

    @classmethod
    def enumerate_normalized(cls, nb_nodes, forbidden_classes=None):
        if forbidden_classes is None:
            forbidden_classes = []
        if not nb_nodes:
            return
        elif nb_nodes == 1:
            if not Bot in forbidden_classes:
                yield Bot()
            if not Top in forbidden_classes:
                yield Top()
        else:
            for split in range(1,nb_nodes-1, 2):
                # Generating Parrs
                if Parr not in forbidden_classes:
                    for a in cls.enumerate_normalized(split, [Bot,Parr]):
                        for b in cls.enumerate_normalized(nb_nodes - split - 1, [Bot]):
                            yield Parr(a,b)
                # Generating Tensors
                if Tens not in forbidden_classes:
                    for a in cls.enumerate_normalized(split, [Top,Tens]):
                        for b in cls.enumerate_normalized(nb_nodes - split - 1, [Top]):
                            yield Tens(a,b)

class NullaryFormula(Formula):
    @property
    def depth(self):
        return 0

    def walk(self):
        yield self

    def normalized(self):
        return True

class Top(NullaryFormula):
    def to_string(self):
        return "I"

    def valuation(self):
        return 1

I = Top()

class Bot(NullaryFormula):
    def to_string(self):
        return "⟂"

    def valuation(self):
        return 0

b = Bot()

class BinaryFormula(Formula):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def depth(self):
        return 1 + max([self.a.depth, self.b.depth])


class NullaryFormula(Formula):
    @property
    def depth(self):
        return 0

    def walk(self):
        yield self

    def normalized(self):
        return True

class Top(NullaryFormula):
    def to_string(self):
        return "I"

    def valuation(self):
        return 1

I = Top()

class Bot(NullaryFormula):
    def to_string(self):
        return "⟂"

    def valuation(self):
        return 0

b = Bot()

class BinaryFormula(Formula):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def depth(self):
        return 1 + max([self.a.depth, self.b.depth])

    def walk(self):
        yield self
        yield from self.a.walk()
        yield from self.b.walk()

class Parr(BinaryFormula):
    def to_string(self):
        return "{}&{}".format(self.a.to_string_with_brackets(),
                              self.b.to_string_with_brackets())

    def valuation(self):
        return self.a.valuation() + self.b.valuation()

    def normalized(self):
        return (self.a != Bot() and self.b != Bot() and
                self.a.normalized() and self.b.normalized())

class Tens(BinaryFormula):
    def to_string(self):
        return "{}x{}".format(self.a.to_string_with_brackets(),
                              self.b.to_string_with_brackets())

    def valuation(self):
        return self.a.valuation() - 1 + self.b.valuation()

    def normalized(self):
        return (self.a != Top() and self.b != Top() and
                self.a.normalized() and self.b.normalized())


