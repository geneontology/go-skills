"""Dump a GO-CAM model for QC: metadata, individuals, every fact with its evidence (code|reference|with),
comments, and automatic hygiene flags.

Usage:
  uv run --with rdflib python ${CLAUDE_SKILL_DIR}/scripts/gocam_dump.py model.ttl      # Noctua OWL/Turtle export or noctua-models TTL
  uv run --with rdflib python ${CLAUDE_SKILL_DIR}/scripts/gocam_dump.py model.json     # barista export-model (minerva JSON)

Individual IRIs are shortened to their last 4 characters (…1234), the handle used in the QC report.
The flags are mechanical; every one still needs a curator-level reading (see references/qc-checks.md).
"""
import sys, json, re, collections, pathlib

LEGO = "http://geneontology.org/lego/"
OK_PREFIXES = ("PMID", "GO_REF", "DOI", "Reactome", "ISBN")


def short(u):
    u = str(u)
    for p, r in [("http://purl.obolibrary.org/obo/", ""), ("http://identifiers.org/uniprot/", "UniProtKB:"), ("http://identifiers.org/", "")]:
        if u.startswith(p): u = r + u[len(p):]
    if u.startswith("http://model.geneontology.org/") or u.startswith("gomodel:"): return "…" + u[-4:]
    return u.replace("_", ":", 1) if "_" in u and ":" not in u.split("_")[0] else u


def load_ttl(path):
    import rdflib
    from rdflib.namespace import RDF, RDFS, OWL
    g = rdflib.Graph(); g.parse(path, format="turtle")
    DC = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    EV, WITH = rdflib.URIRef(LEGO + "evidence"), rdflib.URIRef(LEGO + "evidence-with")
    onto = next(g.subjects(RDF.type, OWL.Ontology))
    meta = [(str(p).split("/")[-1].split("#")[-1], str(o)) for p, o in g.predicate_objects(onto) if p not in (RDF.type, OWL.versionIRI)]
    inds = {str(i): [short(t) for t in g.objects(i, RDF.type) if t != OWL.NamedIndividual] for i in g.subjects(RDF.type, OWL.NamedIndividual)}
    ev = {}
    for i, t in inds.items():
        if any(x.startswith("ECO:") for x in t):
            n = rdflib.URIRef(i)
            ev[i] = dict(code=",".join(t), refs=[str(o) for o in g.objects(n, DC.source)],
                         withs=[w for o in g.objects(n, WITH) for w in re.split(r"[|,]\s*", str(o)) if w],
                         comments=[str(c) for c in g.objects(n, RDFS.comment)])
    axev, axcom = collections.defaultdict(list), collections.defaultdict(list)
    for ax in g.subjects(RDF.type, OWL.Axiom):
        k = tuple(str(x) for x in (g.value(ax, OWL.annotatedSource), g.value(ax, OWL.annotatedProperty), g.value(ax, OWL.annotatedTarget)))
        axev[k].append([str(e) for e in g.objects(ax, EV)])
        axcom[k].extend(str(c) for c in g.objects(ax, RDFS.comment))
    facts = []
    for a, b, c in g:
        a, b, c = str(a), str(b), str(c)
        if a in inds and c in inds and a not in ev and c not in ev and b.startswith("http://purl.obolibrary.org/obo/"):
            groups = axev.get((a, b, c), [])
            facts.append(dict(s=a, p=short(b), o=c, ev=[e for grp in groups for e in grp], n_axioms=len(groups), comments=axcom.get((a, b, c), [])))
    icom = {i: [str(c) for c in g.objects(rdflib.URIRef(i), RDFS.comment)] for i in inds}
    return meta, inds, ev, facts, icom


def load_minerva(path):
    d = json.loads(pathlib.Path(path).read_text())
    d = d.get("data", d)
    ann = lambda x, k: [a["value"] for a in x.get("annotations", []) if a["key"] == k]
    meta = [(a["key"], a["value"]) for a in d.get("annotations", []) if not a["key"].startswith("hint")]
    inds, ev, icom = {}, {}, {}
    for i in d["individuals"]:
        types = [t.get("id") or ("NOT " + t["filler"]["id"] if t.get("type") == "complement" else "?") for t in i["type"]]
        inds[i["id"]] = types
        icom[i["id"]] = ann(i, "comment")
        if any(t.startswith("ECO:") for t in types):
            ev[i["id"]] = dict(code=",".join(types), refs=ann(i, "source"),
                               withs=[w for v in ann(i, "with") for w in re.split(r"[|,]\s*", v) if w], comments=ann(i, "comment"))
    facts = [dict(s=f["subject"], p=f["property"], o=f["object"], ev=ann(f, "evidence"), n_axioms=1, comments=ann(f, "comment")) for f in d["facts"]]
    return meta, inds, ev, facts, icom


def main(path):
    meta, inds, ev, facts, icom = (load_minerva if path.endswith(".json") else load_ttl)(path)
    lab = lambda i: ",".join(inds.get(i, [short(i)])) + f"[{short(i)}]"
    cls = lambda i: inds.get(i, [""])[0] if inds.get(i) else ""
    flags = []
    print("== METADATA")
    for k, v in meta: print(f"  {k} = {v}")
    title = next((v for k, v in meta if k == "title"), "")
    print(f"== COUNTS individuals={len(inds) - len(ev)} evidence={len(ev)} facts={len(facts)}")
    print("== INDIVIDUALS"); [print("  ", lab(i)) for i in sorted(inds, key=str) if i not in ev]
    print(f"== FACTS ({len(facts)})  format: subject --relation--> object :: code|reference|with")
    used = set()
    for f in sorted(facts, key=lambda f: (lab(f["s"]), f["p"])):
        used.update(f["ev"])
        where = f"{lab(f['s'])} --{f['p']}--> {lab(f['o'])}"
        es = "; ".join(f"{ev[x]['code']}|{'/'.join(ev[x]['refs'])}|{'/'.join(ev[x]['withs'])}" for x in f["ev"] if x in ev) or "NO EVIDENCE"
        print(f"  {where}  ::  {es}")
        for c in f["comments"]: print(f"      comment: {c}")
        if not f["ev"]: flags.append(("no-evidence", where))
        if f["n_axioms"] > 1: flags.append(("duplicated-evidence-axiom", where))
        for x in f["ev"]:
            e = ev.get(x)
            if not e: continue
            code, refs, withs = e["code"], e["refs"], e["withs"]
            tag = f"{where} [{code}|{'/'.join(refs)}|{'/'.join(withs)}]"
            if code == "ECO:0000305" and not withs: flags.append(("IC-without-with", tag))
            if code in ("ECO:0000250", "ECO:0000266") and not withs: flags.append(("ISS/ISO-without-with", tag))
            if withs and cls(f["o"]) in withs: flags.append(("with-equals-asserted-object (circular)", tag))
            if withs and code == "ECO:0000305" and cls(f["s"]) in withs and f["p"] in ("RO:0002333",): flags.append(("with-equals-subject-MF on enabled-by", tag))
            if "GO_REF:0000024" in refs and code != "ECO:0000250": flags.append(("GO_REF:0000024 (ISS recipe) with non-ISS code", tag))
            if "GO_REF:0000036" in refs and code != "ECO:0000305": flags.append(("GO_REF:0000036 (IC recipe) with non-IC code", tag))
            if code in ("ECO:0000314", "ECO:0000315", "ECO:0000353", "ECO:0000316", "ECO:0000270") and withs and f["p"] not in ("RO:0002233",):
                flags.append(("experimental code with a 'with' (check)", tag))
            for r in refs:
                if r.split(":")[0] not in OK_PREFIXES: flags.append(("malformed-reference", f"{r} on {where}"))
            if code in ("ECO:0000314", "ECO:0000315", "ECO:0000353", "ECO:0000316") and not any(r.startswith(("PMID", "DOI")) for r in refs):
                flags.append(("experimental code without a paper", tag))
    print("== COMMENTS on individuals")
    for i, cs in icom.items():
        for c in cs: print("  ", lab(i), "::", c)
    model_comments = [v for k, v in meta if k == "comment"]
    inv = {x for f in facts for x in (f["s"], f["o"])}
    for e in ev:
        if e not in used: flags.append(("disconnected-evidence", short(e)))
    for i in inds:
        if i not in inv and i not in ev: flags.append(("individual-in-no-fact", lab(i)))
    if len(title) > 60: flags.append(("title-longer-than-60", f"{len(title)} chars: {title}"))
    if not re.search(r"\([A-Z][a-z]+.*\)\s*$", title): flags.append(("title-without-(Species)", title))
    for c in model_comments: flags.append(("model-comment-present (remove reviewer notes once answered?)", c[:120]))
    refs = sorted({r for e in ev.values() for r in e["refs"]})
    print("== REFERENCES:", refs)
    classes = sorted({t for i, ts in inds.items() if i not in ev for t in ts if re.match(r"^(GO|CL|UBERON|CHEBI|PR|ECO):", t)})
    print("== ONTOLOGY CLASSES (check labels + obsoletion):", classes)
    genes = sorted({t for ts in inds.values() for t in ts if not re.match(r"^(GO|CL|UBERON|CHEBI|ECO):", t)})
    print("== ENTITIES (gene products, complexes, PR):", genes)
    withs = sorted({w for e in ev.values() for w in e["withs"]})
    print("== WITH values (check each ortholog has a source annotation; each GO with is a real supporting annotation):", withs)
    print(f"== FLAGS ({len(flags)})")
    for k, v in flags: print(f"  [{k}] {v}")


if __name__ == "__main__":
    main(sys.argv[1])
