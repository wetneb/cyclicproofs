

class DiskPartition(object):
    def __init__(self, links, nodes_order=None):
        """
        :param links: list of pairs of ints, denoting the edges
        :param nodes_order: if provided, specifies the cyclic order on the nodes
        """
        self.links = links
        if nodes_order is not None:
            self.nodes_order = nodes_order
        else:
            unsorted_nodes = set(a for a, _ in links) | set(b for _, b in links)
            self.nodes_order = sorted(unsorted_nodes)

    def to_idx_pair(self, pair):
        a, b = pair
        a_idx = self.nodes_order.index(a)
        b_idx = self.nodes_order.index(b)
        return (min(a_idx, b_idx), max(a_idx, b_idx))

    def is_planar(self):
        """
        Is this disk partition planar?

        >>> DiskPartition([(0,1),(2,3)]).is_planar()
        True
        >>> DiskPartition([(0,2),(1,3)]).is_planar()
        False
        >>> DiskPartition([(0,1),(1,2)]).is_planar()
        True
        >>> DiskPartition([(1,6),(2,4),(3,7),(4,5)]).is_planar()
        False
        >>> DiskPartition([(1,2),(2,3),(3,4),(4,5),(5,6),(6,7)]).is_planar()
        True
        >>> DiskPartition([(1,2),(2,3),(3,7),(6,7),(6,5),(5,4)]).is_planar()
        True
        """
        if len(self.links) <= 1:
            return True
        else:
            splitting_link = self.links[0]
            a, b = self.to_idx_pair(splitting_link)

            inside_links = []
            outside_links = []
            for link in self.links[1:]:
                u, v = self.to_idx_pair(link)
                u_inside = a <= u and u <= b
                v_inside = a <= v and v <= b
                u_outside = u <= a or b <= u
                v_outside = v <= a or b <= v
                if u_inside and v_inside:
                    inside_links.append(link)
                elif u_outside and v_outside:
                    outside_links.append(link)
                else:
                    return False

            # the split was successfull, recurse
            inside_disk = DiskPartition(inside_links, self.nodes_order[a:b+1])
            outside_disk = DiskPartition(outside_links, self.nodes_order[:a+1] + self.nodes_order[b:])
            return inside_disk.is_planar() and outside_disk.is_planar()

