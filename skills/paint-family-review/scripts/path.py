# usage: python3 path.py treefull.json ACC [ACC...]  -> ancestor path (node, event, species, sf, nleaves) for each UniProt leaf
import json,sys,re
d=json.load(open(sys.argv[1])); want=set(sys.argv[2:])
def kids(x):
    c=x.get('children')
    if not c: return []
    c=c['annotation_node']; return c if isinstance(c,list) else [c]
def nleaves(x):
    k=kids(x); return 1 if not k else sum(nleaves(y) for y in k)
def walk(x,p):
    k=kids(x)
    if not k:
        m=re.search(r'UniProtKB=(\w+)',x.get('node_name',''))
        if m and m.group(1) in want:
            print('==',m.group(1),x.get('gene_symbol'),x.get('organism'),x.get('persistent_id'))
            for n in p: print('   ',n.get('persistent_id'),n.get('event_type'),n.get('species') or '',n.get('sf_id') or '',nleaves(n))
    for y in k: walk(y,p+[x])
walk(d['search']['tree_topology']['annotation_node'],[])
