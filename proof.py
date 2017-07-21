from rbgraph import *

R = RBG
B = RBG
r = R()
b = B()

def enumerate_proofs(limit):
    reachable = {}
    reachable[0] = {RBG(RBG()):1}

    all_reachables = {RBG(RBG())}

    # fill each set of reacheable terms after m merges
    for m in range(1,limit+1):
        reachable[m] = dict()
        # select a previous number of merges for the LHS
        for p in range(0,m):
            # loop through existing proofs for the LHS
            for lhs in reachable[p]:
                # loop through existing proofs for the RHS
                for rhs in reachable[m-1-p]:
                    # loop through possible positions
                    for i in range(len(lhs)):
                        for j in range(len(lhs)+1):
                            for k in range(len(rhs)):
                                for l in range(len(rhs)+1):
                                    reach = lhs.merge(rhs,i,j,k,l)
                                    if reach in reachable[m]:
                                        reachable[m][reach] += 1
                                    elif not reach in all_reachables:
                                        reachable[m][reach] = 1
                                        all_reachables.add(reach)

        print('------{}------'.format(m))
        for term, count in reachable[m].items():
            if term == B(R(B(R(b,b),r),b),r,R(b,B(r,r))):
                print('triple unit:')
            print('{}\t{}'.format(count,term))

if __name__ == '__main__':
    import sys
    enumerate_proofs(int(sys.argv[1]))
