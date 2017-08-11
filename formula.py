
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

class NullaryFormula(Formula):
    @property
    def depth(self):
        return 0

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


class Parr(BinaryFormula):
    def to_string(self):
        return "{}&{}".format(a.to_string_with_brackets(),
                              b.to_string_with_brackets())

class Tens(BinaryFormula):
    def to_string(self):
        return "{}x{}".format(a.to_string_with_brackets(),
                              b.to_string_with_brackets())




