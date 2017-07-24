from rbgraph import *
from collections import defaultdict

R = RBG
B = RBG
r = R()
b = B()
triple_unit =  B(R(B(R(b,b),r),b),r,R(b,B(r,r)))

def enumerate_proofs(limit):
    reachable = {}
    reachable[0] = {RBG(RBG()):1}

    all_reachables = {RBG(RBG())}

    backtrack = defaultdict(list)
    # structure of this dict:
    # term -> list of (lhs,rhs,i,j,k,l)

    # fill each set of reacheable terms after m merges
    for m in range(1,limit+1):
        reachable[m] = {}
        # select a previous number of merges for the LHS
        for p in range(0,m):
            # loop through existing proofs for the LHS
            for lhs, num_lhs in reachable[p].items():
                # loop through existing proofs for the RHS
                for rhs, num_rhs in reachable[m-1-p].items():
                    # loop through possible positions
                    for i in range(len(lhs)):
                        for j in range(len(lhs)+1):
                            for k in range(len(rhs)):
                                for l in range(len(rhs)+1):
                                    term = lhs.merge(rhs,i,j,k,l)
                                    new_term = term not in all_reachables
                                    if term in reachable[m]:
                                        reachable[m][term] += num_lhs * num_rhs
                                        backtrack[term]
                                    elif new_term:
                                        reachable[m][term] = num_lhs * num_rhs
                                        all_reachables.add(term)

                                    if term in reachable[m]:
                                        backtrack[term].append(
                                            (lhs,rhs,i,j,k,l))

        print('------{}------'.format(m))
        for term, count in reachable[m].items():
            if term == triple_unit:
                print('triple unit:')
            print('{}\t{}'.format(count,term))
    return backtrack

class ProofStep(object):
    def __init__(self, terms):
        self.terms = terms

class UnitAxiom(ProofStep):
    def __repr__(self):
        return "unit"

class MergeStep(ProofStep):
    def __init__(self, terms, coords):
        super(MergeStep, self).__init__(terms)
        self.coords = coords
    def __repr__(self):
        return "merge at {}".format(self.coords)

def reconstruct_proofs(left, term, proof_of_left, backtrack):
    """
    Prints all proofs of a given term, at the context [left, X, right]
    """
    if term == B(r):
        yield proof_of_left + [UnitAxiom(left + [term])]
    else:
        for lhs,rhs,i,j,k,l in backtrack[term]:
            proofs_of_lhs = reconstruct_proofs(left, lhs, proof_of_left, backtrack)
            for proof_of_lhs in proofs_of_lhs:
                proofs_of_rhs = reconstruct_proofs(left + [lhs], rhs, proof_of_lhs, backtrack)
                for proof_of_rhs in proofs_of_rhs:
                    yield proof_of_rhs + [MergeStep(left + [term], (i,j,k,l))]

def print_proofs(iterable_of_proofs):
    f = open('output/index.html', 'w')
    for idx, proof in enumerate(iterable_of_proofs):
        f.write('<div style="display: inline-block; padding: 30px; border-right: 1px solid grey;">\n')
        f.write('<h3>Proof {}</h3>\n'.format(idx))
        print('---- Proof {} -----'.format(idx))
        for j, step in enumerate(proof):
            print('  '.join(str(term) for term in step.terms))
            name = 'img/{}-{}'.format(idx, j)
            RBG.to_graphs(step.terms, 'output/'+name)
            f.write('<p>{}</p>'.format(step))
            f.write('<img src="{}.png" /><br />\n'.format(name))
        f.write('</div>\n')
        print
    f.close()

if __name__ == '__main__':
    import sys
    mygraph = B(R(b,B(R(b,B(R(b,b),r,r)),r)),r)
    backtrack = enumerate_proofs(int(sys.argv[1]))
    proofs = reconstruct_proofs([], mygraph, [], backtrack)
    print_proofs(proofs)


