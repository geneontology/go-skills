# usage: kmerhit.py query.fa db.fa  -> top hits by shared 5-mer fraction
import sys
def rd(f):
    d={};k=None
    for l in open(f):
        l=l.strip()
        if l.startswith('>'): k=l[1:].split()[0]; d[k]=''
        elif k: d[k]+=l
    return d
q=rd(sys.argv[1]); db=rd(sys.argv[2]); K=5
def km(s): return set(s[i:i+K] for i in range(len(s)-K+1))
dbk={k:km(v) for k,v in db.items()}
for n,s in q.items():
    qk=km(s)
    hits=sorted(((len(qk&v)/max(1,len(qk)),k) for k,v in dbk.items()),reverse=True)[:3]
    print(n,len(s),' '.join('%s:%.2f'%(k,f) for f,k in hits))
