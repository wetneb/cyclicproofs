from rbgraph import *
from collections import defaultdict
from proofstep import UnitAxiom, MergeStep
from proof import Proof

triple_unit =  B(R(B(R(b,b),r),b),r,R(b,B(r,r)))

def print_proofs(iterable_of_proofs, name):
    f = open('output/{}.html'.format(name), 'w')
    for idx, proof in enumerate(iterable_of_proofs):
        f.write('<div style="display: inline-block; padding: 30px; border-right: 1px solid grey;">\n')
        f.write('<h3>Proof {}</h3>\n'.format(idx))
        f.write(proof.to_html())
        f.write('</div>\n')
    f.close()

if __name__ == '__main__':
    import sys
    mygraph = B(R(b,B(R(b,B(R(b,b),r,r)),r)),r)
    pspace = B(R(b,b),r,r,r,R(b,b))
    four = B(R(b,b),r,r,R(b,b),r)
    backtrack = Proof.enumerate(int(sys.argv[1]))
    proofs = Proof.reconstruct((), triple_unit, Proof(), backtrack)
    proofs = list(proofs)
    a = proofs[0].remove_unit_intros()
    b = proofs[1].remove_unit_intros()
    path = b.equivalence_path(a)
    print_proofs(path, 'equivalence')


