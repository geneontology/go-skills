# usage: report_build.py file.md  -> file.html + A4 PDF next to it (needs markdown, xhtml2pdf)
import sys, markdown
from xhtml2pdf import pisa
src=sys.argv[1]; base=src[:-3]
body=markdown.markdown(open(src).read(), extensions=['tables','sane_lists'])
css="""@page{size:A4;margin:16mm 14mm}
body{font-family:Arial,sans-serif;font-size:9.5pt;line-height:1.35;color:#222}
h1{font-size:16pt;border-bottom:2px solid #2b5797;padding-bottom:4px;color:#2b5797}
h2{font-size:13pt;color:#2b5797;margin-top:18px}
h3{font-size:11pt;margin:12px 0 4px}
table{border-collapse:collapse;width:100%;margin:4px 0 8px}
th,td{border:1px solid #bbb;padding:3px 5px;vertical-align:top;text-align:left}
th{background:#e8eef7}"""
html=f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{base}</title><style>{css}</style></head><body>{body}</body></html>"
open(base+'.html','w').write(html)
safe=html.replace('→','-&gt;').replace('—','-').replace('–','-').replace('·','|')
with open(base+'.pdf','wb') as f: pisa.CreatePDF(safe,dest=f)
