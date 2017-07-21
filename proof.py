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

def reconstruct_proofs(left, term, proof_of_left, backtrack):
    """
    Prints all proofs of a given term, at the context [left, X, right]
    """
    if term == B(r):
        yield proof_of_left + [left + [term]]
    else:
        for lhs,rhs,i,j,k,l in backtrack[term]:
            proofs_of_lhs = reconstruct_proofs(left, lhs, proof_of_left, backtrack)
            for proof_of_lhs in proofs_of_lhs:
                proofs_of_rhs = reconstruct_proofs(left + [lhs], rhs, proof_of_lhs, backtrack)
                for proof_of_rhs in proofs_of_rhs:
                    yield proof_of_rhs + [left + [term]]

def print_proofs(iterable_of_proofs):
    for idx, proof in enumerate(iterable_of_proofs):
        print('---- Proof {} -----'.format(idx))
        for step in proof:
            print('  '.join(str(term) for term in step))
        print

if __name__ == '__main__':
    import sys
    backtrack = enumerate_proofs(int(sys.argv[1]))
    proofs = reconstruct_proofs([], triple_unit, [], backtrack)
    print_proofs(proofs)


