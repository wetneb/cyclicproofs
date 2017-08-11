
class Formula(object):
    
    def to_string(self):
        raise NotImplementedError()

    @property
    def depth(self):
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
        for i, subformula in enumerate(self):
            if i == idx:
                return subformula
        raise ValueError("Index is out of bounds")

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


class NullaryFormula(Formula):
    @property
    def depth(self):
        return 0

    def walk(self):
        yield self 

class Top(NullaryFormula):
    def to_string(self):
        return "I"

I = Top()

class Bot(NullaryFormula):
    def to_string(self):
        return "⟂"
    
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

class Tens(BinaryFormula):
    def to_string(self):
        return "{}x{}".format(self.a.to_string_with_brackets(),
                              self.b.to_string_with_brackets())




