from formula import Tens, Parr, Bot, Top

class Switching(object):
    def __init__(self, linking, directions):
        self.linking = linking
        self.formula = linking.formula
        self.directions = directions
        self.parent_map = self.formula.parent_map()

    def browse(self, current=0, coming_from=None):
        """
        Walks on the linking with that switching.

        This is a generator of indices.
        If there is a cycle, this generator will be infinite!
        We also assume that the linking is syntactically_valid.
        """
        f = self.formula[current]
        yield current

        neighbours = []

        parent_idx = self.parent_map.get(current)
        if parent_idx is not None:
            parent_f = self.formula[parent_idx]
            enabled = (not isinstance(parent_f, Parr) or
                    (self.directions[parent_idx] ==
                     (parent_idx + 1 == current)))
            if enabled:
                neighbours.append(parent_idx)

        # Case of units
        if current in self.linking.forward:
            neighbours.append(self.linking.forward[current])
        if current in self.linking.backward:
            neighbours += self.linking.backward[current]

        # Case of a Tensor
        if isinstance(f, Tens):
            neighbours.append(current + 1)
            neighbours.append(current + len(f.a) + 1)
        # Case of a Parr
        elif isinstance(f, Parr):
            if self.directions[current]: # Left
                neighbours.append(current + 1)
            else: # Right
                neighbours.append(current + len(f.a) + 1)

        # Recurse
        for neighbour in neighbours:
            if neighbour != coming_from:
                yield from self.browse(neighbour, coming_from=current)

    def acyclic_and_connected(self):
        """
        Is the switching acyclic and connected?
        """
        seen = set()
        for index in self.browse():
            if index in seen:
                return False
            seen.add(index)
        return len(seen) == len(self.formula)

    @classmethod
    def enumerate(cls, linking, only_parr=True):
        formula = linking.formula
        valid_connectives = [Parr]
        if not only_parr:
            valid_connectives.append(Tens)
        parr_indices = [
            idx
            for idx, subformula in enumerate(formula)
            if any(isinstance(subformula, node)
                    for node in valid_connectives)
        ]
        bound = pow(2, len(parr_indices))
        for i in range(bound):
            remainder = i
            dct = {}
            for idx in parr_indices:
                dct[idx] = (remainder % 2 == 1)
                remainder // 2
            yield cls(linking, dct)


    def long_trip(self, cur_idx=0, cur_dir=True, coming_from=None):
        """
        Enumerates the long trip for this switching.
        """
        if cur_idx is None:
            return

        if coming_from is not None:
            yield (coming_from, cur_idx, cur_dir)

        f = self.formula[cur_idx]
        left = self.directions.get(cur_idx, True)
        parent_idx = self.parent_map.get(cur_idx)
        coming_from_left = coming_from == cur_idx + 1

        if isinstance(f, Bot):
            if cur_dir: # Going upwards
                yield from self.long_trip(self.linking.forward[cur_idx], False, cur_idx)
            else: # going downwards
                yield from self.long_trip(parent_idx, False, cur_idx)
        elif isinstance(f, Top):
            if cur_dir: # Going upwards
                for bot in self.linking.backward[cur_idx]:
                    yield from self.long_trip(bot, False, cur_idx)
            else: # going downwards
                yield from self.long_trip(parent_idx, False, cur_idx)
        elif isinstance(f, Tens):
            if cur_dir: # Going upwards
                if left:
                    yield from self.long_trip(cur_idx + 1 + len(f.a), True, cur_idx)
                else:
                    yield from self.long_trip(cur_idx + 1, True, cur_idx)
            else:
                if left == coming_from_left:
                    yield from self.long_trip(parent_idx, False, cur_idx)
                elif left:
                    yield from self.long_trip(cur_idx + 1, True, cur_idx)
                else:
                    yield from self.long_trip(cur_idx + 1 + len(f.a), True, cur_idx)
        elif isinstance(f, Parr):
            if cur_dir: # upwards
                if left:
                    yield from self.long_trip(cur_idx + 1, True, cur_idx)
                else:
                    yield from self.long_trip(cur_idx + 1 + len(f.a), True, cur_idx)
            else: # downwards
                if left == coming_from_left:
                    yield from self.long_trip(parent_idx, False, cur_idx)
                else: # back to the sender
                    yield from self.long_trip(coming_from, True, cur_idx)


    def long_trip_criterion(self):
        """
        Does the long trip associated to this switching encounter
        every edge in each direction exactly once?
        """
        f = self.formula
        number_edges = len(f) - 1 + len([ subf for subf in f if isinstance(subf, Bot)])
        seen_edges = {}
        for a, b, _ in self.long_trip():
            seen = seen_edges.get((b,a), 0)
            if seen:
                if seen != 1:
                    return False
                seen_edges[(b,a)] = 2
            elif (a,b) in seen_edges:
                return False
            else:
                seen_edges[(a,b)] = 1

        return all(v == 2 for v in seen_edges.values()) and len(seen_edges) == number_edges

    def stack_criterion(self):
        """
        Implements the stack criterion of Nagayama & Okada
        """
        stack = []
        previous_edge = None
        try:
            for a, b, d in self.long_trip():
                fa = self.formula[a]
                if (b,a) == previous_edge:
                    stack.append(fa)
                else:
                    fa = self.formula[a]
                    if isinstance(fa, Parr) and not d: # traversing a Parr downwards
                        rhs = fa
                        top = stack.pop()
                        if rhs != top:
                            return False

                previous_edge = (a,b)
            return stack == [self.formula]
        except IndexError:
            return False


    @classmethod
    def special(cls, linking):
        """
        Returns the special switching that the
        special trip is built on
        (left switching for Parr, right switching
        for Tens).
        """
        dct = {}
        for idx, subformula in enumerate(linking.formula):
            if isinstance(subformula, Tens):
                dct[idx] = False
            elif isinstance(subformula, Parr):
                dct[idx] = True
        return cls(linking, dct)

