
"""
Defines red-blue graphs
"""

class RBG(object):
    def __init__(self, *children):
        self.children = list(children)
        self.size = 1 + sum(child.size for child in self.children)

    def __getitem__(self, key):
        # our sequents are cyclic
        if type(key) == int:
            return self.children[key % len(self.children)]
        else: # assuming a pair of ints: starting index and length
            # treat the case where they are equal separately
            start, length = key
            if length == 0: # interpreting as an empty subsequence
                return RBG()
            start = start % len(self)
            return RBG(*[ self[i] for i in range(start, start + length)])

    def __len__(self):
        return len(self.children)

    def __eq__(self, other):
        if self.size != other.size:
            return False

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

    def __hash__(self):
        return self.size

    def units(self, blue=False):
        """
        Number of units of the given color
        """
        if not self.children and blue:
            return 1
        else:
            return sum(child.units(blue=not blue) for child in self.children)

    def __add__(self, other):
        return RBG(*(self.children + other.children))

    def merge(self, other, i=0, j=0, k=0, l=0):
        """
        Given another graph, and indices
        0 <= i < len(self) (position in self)
        0 <= j <= len(self) (length in self)
        0 <= k < len(self) (position in other)
        0 <= l <= len(self) (length in other)

        Returns the merged graph obtained by joining
        the subgraphs self[i,j], self[k,l] by a red node
        """
        red_left = self[i,j]
        left_list = red_left[0].children if len(red_left) == 1 else [red_left]
        red_right = other[k,l]
        right_list = red_right[0].children if len(red_right) == 1 else [red_right]

        red_fragment = RBG(RBG(*(left_list + right_list)))
        if len(left_list) + len(right_list) == 1:
            # simplify red unitality
            red_fragment = sum(left_list, RBG()) + sum(right_list, RBG())
        #print('red fragment')
        #print(red_fragment)

        blue_left = self[i+j,len(self)-j]
        blue_right = other[k+l,len(other)-l]
        #print('blue lists')
        #print(blue_right + blue_left)
        return red_fragment + blue_right + blue_left

    def __repr__(self, start_color='B'):
        if len(self) == 0:
            return start_color.lower()
        else:
            return '{}({})'.format(start_color,
                    ','.join(c.__repr__('R' if start_color=='B' else 'B')
                    for c in self.children))
