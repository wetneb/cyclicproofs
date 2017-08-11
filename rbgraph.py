
"""
Defines red-blue graphs
"""

class RBG(object):
    def __init__(self, *children):
        self.children = list(children)
        self.size = 1 + sum(child.size for child in self.children)
        # the self.links list contains pairs of indices:
        # (i,j) means that blue unit i is linked to red unit j
        # indices are counted just like in the to_graph function.
        self.links = []

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

    def __eq__(self, other, cyclic=True):
        if self.size != other.size:
            return False

        # try to match self to other
        if len(self) != len(other):
            return False
        if cyclic:
            # if matching in cyclic mode,
            # try all the possible offsets
            offsets = range(len(self))
        else:
            # otherwise, just zero
            offsets = [0]

        for offset in offsets:
            matching = all(
                self[i].__eq__(other[i+offset], cyclic=False)
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

        blue_left = self[i+j,len(self)-j]
        blue_right = other[k+l,len(other)-l]

        # TODO: handle simplification case in unit translation
        size_red_left = red_left.number_of_nodes()
        size_blue_right = blue_right.number_of_nodes()
        size_other = other.number_of_nodes()
        final_graph = red_fragment + blue_right + blue_left
        final_graph.links = []
        final_graph.links += self.translate_links(i, j, 2, 1 + size_other + size_red_left)
        final_graph.links += other.translate_links(k, l, 2 + size_red_left, 1 + size_red_left + size_blue_right)
        return final_graph

    def possible_merges(self, rhs):
        for i in range(len(self)):
            for j in range(len(self)+1):
                for k in range(len(rhs)):
                    for l in range(len(rhs)+1):
                        term = self.merge(rhs,i,j,k,l)
                        yield (term,i,j,k,l)

    def number_of_nodes(self):
        """
        Returns the number of nodes in this graph
        """
        return 1 + sum(c.number_of_nodes()
                for c in self.children)

    def build_translation(self, i, j, offset_in, translation):
        """
        Populates the unit translation dictionary for the slice [i,j]
        of this graph, with the given offset.
        """
        size_before_in = self[0,i].number_of_nodes()
        cur_idx = size_before_in
        rel_idx = 1
        for idx in range(i,i+j):
            if idx % len(self) == 0:
                cur_idx = 1
            old_idx = cur_idx
            offset = rel_idx - size_before_in + offset_in
            cur_idx = self[idx]._build_translation_dict(cur_idx, offset, translation)
            rel_idx += cur_idx - old_idx

    def translate_links(self, i, j, offset_in, offset_out):
        """
        Translates unit links to their new indices, assuming
        that the graph is split into two regions (for a merge).

        Two offsets are given for each region.
        """
        translation = {}
        self.build_translation(i, j, offset_in, translation)
        self.build_translation(i+j % len(self), len(self)-j, offset_out, translation)

        return [
            (translation[a],translation[b])
            for a, b in self.links
        ]

    def _build_translation_dict(self, start_idx, offset, dct):
        """
        Adds mappings for units in this graph, assuming the first
        unit we encounter has id start_idx+1 and should be translated with
        the given offset.

        :returns: the last id seen
        """
        cur_idx = start_idx + 1
        if not self.children:
            dct[cur_idx] = cur_idx + offset
        for child in self.children:
            cur_idx = child._build_translation_dict(cur_idx, offset, dct)
        return cur_idx

    def __repr__(self, start_color='B'):
        if len(self) == 0:
            return start_color.lower()
        else:
            return '{}({})'.format(start_color,
                    ','.join(c.__repr__('R' if start_color=='B' else 'B')
                    for c in self.children))

    def to_graph(self, fname):
        import graphviz as gv
        g = gv.Graph()
        self._fill_graph(g, blue=True, idx_start=0)
        g.render(fname)

    def _fill_graph(self, graph, blue, idx_start):
        bgcolor = '#0000ff' if blue else '#ff0000'
        graph.node(str(idx_start), label='', color=bgcolor)
        cur_idx = idx_start + 1
        for child in self.children:
            graph.edge(str(idx_start), str(cur_idx))
            cur_idx = child._fill_graph(graph, not blue, cur_idx)

        return cur_idx

    @classmethod
    def to_graphs(cls, lst, name):
        import graphviz as gv
        g = gv.Graph()
        g.attr('node', shape='circle', style='filled', heigth='0.07', width='0.07', fixedsize='true')
        idx = 0
        for t in lst:
            idx = t._fill_graph(g, blue=True, idx_start=idx)
        g.format = 'png'
        #print(g.source)
        g.render(filename=name)


R = RBG
B = RBG
b = B()
r = R()
