from formula import Tens, Parr

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
            neighbours.append(self.linking.backward[current])

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

