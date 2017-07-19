
"""
Defines red-blue graphs
"""

class RBG(object):
    def __init__(self, *children):
        self.children = sorted(children)

    def __getitem__(self, key):
        # our sequents are cyclic
        if type(key) == int:
            return self.children[key % len(self.children)]
        else: # assuming a pair of ints
            # treat the case where they are equal separately
            start, end = key
            if start == end: # interpreting as an empty subsequence
                return RBG()
            start = start % len(self)
            end = end % len(self)
            if end <= start: # this interprets [0,len(self)] as the full sequence
                end += len(self)
            return RBG(*[ self[i] for i in range(key[0], key[1])])

    def __len__(self):
        return len(self.children)

    def __eq__(self, other):
        # try to match self to other
        if len(self) != len(other):
            return False
        # try all the possible offsets
        for offset in range(len(self)):
            matching = all(
                self[i] == other[i+offset]
                for i in range(len(self))
            )
            if matching:
                return True

        return len(self) == 0

    def __add__(self, other):
        return RBG(*(self.children + other.children))

    def merge(self, other, i=0, j=0, k=0, l=0):
        """
        Given another graph, and indices
        0 <= i <= j <= len(self)
        0 <= k <= l <= len(self)

        Returns the merged graph obtained by joining
        the subgraphs self[i,j], self[k,l] by a red node
        """
        red_left = self[i,j]
        print(red_left)
        left_list = red_left[0].children if len(red_left) == 1 else [red_left]
        red_right = other[k,l]
        print(red_right)
        right_list = red_right[0].children if len(red_right) == 1 else [red_right]
        print(self[j,i])
        print(other[l,k])
        return self[j,i] + other[l,k] + RBG(RBG(*(left_list + right_list)))

    def __repr__(self):
        if len(self) == 0:
            return 'g'
        else:
            return 'G({})'.format(','.join(str(c) for c in self.children))

