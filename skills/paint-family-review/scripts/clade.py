# usage: clade.py tree.json PTNxxxxxxxxx  -> every leaf under the node: UniProt acc, organism, symbol, definition, last 3 ancestors
import json,sys,re
d=json.load(open(sys.argv[1])); target=sys.argv[2]
root=d['search']['tree_topology']['annotation_node']
def kids(x):
    ch=x.get('children')
    if not ch: return []
    c=ch['annotation_node']; return c if isinstance(c,list) else [c]
def find(x):
    if x.get('persistent_id')==target: return x
    for y in kids(x):
        r=find(y)
        if r: return r
def walk(x,path):
    k=kids(x)
    if not k:
        m=re.search(r'UniProtKB=(\w+)',x.get('node_name',''))
        print(m.group(1) if m else '-', x.get('organism'), x.get('gene_symbol'), x.get('definition'), '>'.join(path[-3:]),sep='\t')
    for y in k: walk(y,path+[(x.get('persistent_id') or '')+':'+(x.get('species') or 'DUP')])
walk(find(root),[])
