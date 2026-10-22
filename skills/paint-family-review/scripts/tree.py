# usage: tree.py tree.json  -> ancestor path of every human leaf, with leaf/organism counts and human members per node
import json,sys
d=json.load(open(sys.argv[1]))
root=d['search']['tree_topology']['annotation_node']
def kids(x):
    ch=x.get('children')
    if not ch: return []
    c=ch['annotation_node']; return c if isinstance(c,list) else [c]
def leaves(x):
    k=kids(x)
    if not k: return [x]
    return [l for y in k for l in leaves(y)]
paths={}
def walk(x,p):
    k=kids(x)
    if not k:
        if x.get('organism')=='Homo sapiens': paths[x['gene_symbol']]=p+[x]
    for y in k: walk(y,p+[x])
walk(root,[])
for g,p in paths.items():
    print('==',g)
    for n in p[:-1]:
        L=leaves(n); orgs=set(l.get('organism') for l in L)
        hs=sorted(l['gene_symbol'] for l in L if l.get('organism')=='Homo sapiens')
        print(' ',n.get('persistent_id'),n.get('event_type'),n.get('species'),n.get('sf_id') or '', 'leaves=%d orgs=%d'%(len(L),len(orgs)), 'human=%s'%','.join(hs))
