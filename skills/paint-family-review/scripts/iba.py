# usage: iba.py annotations.tsv  (QuickGO TSV download; header line optional)
# -> existing IBAs grouped by PANTHER node / aspect / qualifier / GO term, with genes and seeds
import sys,re,collections
d=collections.defaultdict(set); seeds={}
for l in open(sys.argv[1]):
    f=l.rstrip('\n').split('\t')
    if len(f)<10 or f[6]!='ECO:0000318': continue
    m=re.search(r'PANTHER:(PTN\d+)',f[9]); node=m.group(1) if m else '?'
    k=(node,f[5],f[3],f[4]); d[k].add(f[2])
    seeds[k]=[x for x in f[9].split('|') if not x.startswith('PANTHER')]
for k,v in sorted(d.items()):
    print(k[0],k[1],k[2],k[3],'| genes:',','.join(sorted(v))[:100],'| seeds:',','.join(seeds[k])[:160])
