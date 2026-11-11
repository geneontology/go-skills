# usage: outline.py tree.json MIN_LEAVES [PTN]  -> indented node outline (PTN, event, species, SF, n leaves, model-organism genes)
import json,sys
d=json.load(open(sys.argv[1])); minn=int(sys.argv[2]); start=sys.argv[3] if len(sys.argv)>3 else None
MO={'Homo sapiens','Mus musculus','Saccharomyces cerevisiae','Schizosaccharomyces pombe','Arabidopsis thaliana','Drosophila melanogaster','Caenorhabditis elegans','Danio rerio','Dictyostelium discoideum','Escherichia coli','Oryza sativa','Rattus norvegicus','Bacillus subtilis','Pseudomonas aeruginosa'}
def kids(x):
    c=x.get('children')
    if not c: return []
    c=c['annotation_node']; return c if isinstance(c,list) else [c]
def leaves(x):
    k=kids(x); return [x] if not k else [l for y in k for l in leaves(y)]
def find(x):
    if x.get('persistent_id')==start: return x
    for y in kids(x):
        r=find(y)
        if r: return r
def show(x,dep):
    L=leaves(x); k=kids(x)
    mo=sorted(set((l.get('gene_symbol') or '?') for l in L if l.get('organism') in MO))
    if not k: print('  '*dep+'LEAF',x.get('gene_symbol'),x.get('organism')); return
    small=len(L)<minn
    print('  '*dep+'%s %s %s %s n=%d %s'%(x.get('persistent_id'),x.get('event_type'),x.get('species') or '',x.get('sf_id') or '',len(L),','.join(mo)[:300] if (small or len(mo)<15) else '[%d MO genes]'%len(mo)))
    if small: return
    for y in k: show(y,dep+1)
r=d['search']['tree_topology']['annotation_node']
show(find(r) if start else r,0)
