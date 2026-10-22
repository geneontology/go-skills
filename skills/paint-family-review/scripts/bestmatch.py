# usage: bestmatch.py query.fa db.fa  -> top-3 global-alignment identity hits per query (needs Biopython)
import sys
from Bio import SeqIO
from Bio.Align import PairwiseAligner, substitution_matrices
al=PairwiseAligner(); al.substitution_matrix=substitution_matrices.load("BLOSUM62"); al.open_gap_score=-10; al.extend_gap_score=-0.5; al.mode='global'
db=list(SeqIO.parse(sys.argv[2],'fasta'))
for q in SeqIO.parse(sys.argv[1],'fasta'):
    res=[]
    for s in db:
        a=al.align(q.seq,s.seq)[0]
        ident=sum(1 for i,j in zip(*a.aligned) for x,y in zip(range(*i),range(*j)) if q.seq[x]==s.seq[y])
        res.append((ident/max(len(q.seq),len(s.seq)),s.id))
    res.sort(reverse=True); print(q.id[:40],[ (round(r,3),i.split('|')[1]) for r,i in res[:3]])
