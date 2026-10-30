#!/usr/bin/env python3
# Regenerates pdf/acc-en.pdf (+ acc-fr.pdf, same English content) from data/acc.json.
# Usage: python3 tools/gen-fiche-acc.py   (then print with headless Chrome, see footer)
import json, html, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
a = json.load(open(f'{ROOT}/data/acc.json'))

GLOSSARY = [
 ("Asset", "Present economic resource controlled as a result of past events."),
 ("Liability", "Present obligation to transfer an economic resource as a result of past events."),
 ("Shareholders' equity", "Residual interest in assets after deducting liabilities."),
 ("Revenue / expense", "Equity-changing flows, excluding contributions and distributions."),
 ("Accruals", "Revenue and expenses are recognized when earned or incurred, not when cash moves."),
 ("Matching", "Expenses are tied to the revenue they helped produce."),
 ("FIFO / LIFO / WAC", "Inventory cost-flow assumptions: first-in-first-out, last-in-first-out (US GAAP only), weighted average cost."),
 ("Depreciation / amortization / depletion", "Systematic consumption of PP&E, intangibles and natural resources."),
 ("Net book value", "Cost - accumulated depreciation - impairment."),
 ("Impairment", "Carrying amount above recoverable amount = max(fair value - costs of disposal, value in use)."),
 ("Provision", "Liability of uncertain timing or amount: present obligation, probable outflow, reliable estimate."),
 ("Prepaid / accrued expense", "Paid before it relates (asset) / relates before it is paid (liability)."),
 ("Deferred / accrued revenue", "Collected before it is earned (liability) / earned before it is collected (asset)."),
 ("Contribution margin", "Price - variable cost per unit; breakeven = fixed costs / unit margin."),
 ("Relevant cost", "Future cost that differs between options; sunk costs are never relevant."),
 ("Cost pool / allocation base", "Grouping of indirect costs / measurable driver used to allocate them."),
 ("Job vs process costing", "Cost per order or batch / average cost of identical units."),
 ("ABC", "Activity-Based Costing: homogeneous activity pools charged by driver consumption."),
 ("Flexible budget", "Budget recomputed at the actual volume with budgeted prices and unit costs."),
]

def esc(s): return s

css = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; @bottom-center { content: counter(page) " / " counter(pages); font: 9px 'Atkinson Hyperlegible', sans-serif; color: #888; } }
* { box-sizing: border-box; }
body { font: 10.5pt/1.55 'Atkinson Hyperlegible', -apple-system, 'Segoe UI', sans-serif; color: #1c2430; margin: 0; }
.cover { height: 240mm; display: flex; flex-direction: column; justify-content: center; }
.cover .k { font-size: 11pt; letter-spacing: .18em; text-transform: uppercase; color: #7A5C2E; font-weight: 700; }
.cover h1 { font-size: 30pt; margin: 8px 0 4px; line-height: 1.15; }
.cover h2 { font-size: 13pt; font-weight: 400; color: #555; margin: 0 0 22px; }
.cover .meta { border-left: 3px solid #7A5C2E; padding: 6px 14px; color: #444; font-size: 10.5pt; }
h1.ch { page-break-before: always; font-size: 16pt; border-bottom: 2.5px solid #7A5C2E; padding-bottom: 5px; margin: 0 0 4px; }
h1.ch .num { color: #7A5C2E; margin-right: 8px; }
p.readings { color: #666; font-size: 9.5pt; margin: 2px 0 12px; }
h4 { font-size: 11.5pt; margin: 14px 0 4px; color: #20304a; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #d5dae2; padding: 3.5px 6px; text-align: left; vertical-align: top; }
th { background: #f0f2f6; }
.f { font: 9.5pt/1.6 ui-monospace, 'SF Mono', Menlo, monospace; background: #f5f3ee; border: 1px solid #e3ded2; border-left: 3px solid #7A5C2E; border-radius: 5px; padding: 8px 11px; margin: 9px 0; white-space: pre-wrap; }
.key { background: #E6F4EC; border-radius: 6px; padding: 9px 12px; margin: 9px 0; }
.warn { background: #FAF0DC; border-radius: 6px; padding: 9px 12px; margin: 9px 0; }
.def { background: #E7EEFB; border-radius: 6px; padding: 9px 12px; margin: 9px 0; }
.exo { border: 1px solid #d5dae2; border-radius: 8px; padding: 10px 13px; margin: 11px 0; page-break-inside: avoid; }
.exh { margin-bottom: 5px; }
.exsrc { font-size: 8.5pt; color: #777; }
.cg { font-size: 8pt; font-weight: 700; border-radius: 4px; padding: 1px 7px; margin-left: 6px; }
.cg.off { background: #E6F4EC; color: #1D7A4E; }
.cg.prop { background: #FAF0DC; color: #97600C; }
.cgnote { font-size: 9pt; color: #666; }
details.cor { margin-top: 7px; border-top: 1px solid #e2e5ea; padding-top: 6px; }
details.cor > summary { font-weight: 700; color: #7A5C2E; }
details[open] > summary { margin-bottom: 5px; }
details.source-text pre, pre.source-pre { font-size: 7.5pt; white-space: pre-wrap; }
.toc { columns: 2; column-gap: 30px; }
.toc div { margin: 3px 0; break-inside: avoid; }
.assess { background: #f5f3ee; border-radius: 8px; padding: 12px 16px; margin-top: 18px; }
.q { margin: 0 0 10px; page-break-inside: avoid; }
.q .qq { font-weight: 700; }
.q ol { margin: 2px 0 2px 18px; padding: 0; }
.q .ans { color: #1D7A4E; font-weight: 700; }
.q .ex { color: #555; font-size: 9.5pt; }
"""

def cover():
    return f"""<div class="cover"><div class="k">CPTC31081 · ESSEC MiM 1 · Fall 2026</div>
<h1>Refresher Course Accounting</h1><h2>Full revision notes, Class #1 to Class #10</h2>
<div class="meta">Final exam on Tuesday 15 December 2026 in the morning (DOME), on paper: 100% of the grade - financial accounting 60%, management accounting 40%. Four-function calculator only. Resit early 2027.<br>Professor: {html.escape(a['prof'])}.<br>Sources: {html.escape(a['srcnote'])}</div>
<div class="assess"><b>How to use these notes.</b> Each class gives the key concepts, the mechanisms step by step, a worked example and the traps. The practice section of each class has every exercise with its statement and a step-by-step correction (official when published on Moodle, clearly marked "Proposed solution" otherwise). The MCQ annex covers all classes with answers and explanations.</div></div>"""

def toc():
    items = ''.join(f'<div><b>Class #{c[0][1:]}</b> · {html.escape(c[1].split("·")[1].strip())}</div>' for c in a['chapters'])
    return f'<h1 class="ch"><span class="num">§</span>Contents</h1><div class="toc">{items}</div>'

READ = {c[0]: '' for c in a['chapters']}
for cid, note in []:
    pass
INF = dict()
m = re.findall(r'<h4>(Class #\d+)[^<]*</h4><p class="note">([^<]*)</p>', a['infoContent'][0]['en'])
for cls, note in m: INF[cls] = note

def chapters():
    out = []
    for cid, title in a['chapters']:
        body = dict((x[0], x[2]) for x in a['en'])[cid]
        cls = 'Class #' + cid[1:]
        read = INF.get(cls, '')
        ess = dict((x[0], x[1]) for x in a['ess']).get(cid, [])
        essh = ''
        if ess:
            essh = '<div class="key"><b>In one look.</b><ul>' + ''.join(f'<li>{html.escape(str(x))}</li>' for x in ess) + '</ul></div>'
        # open all details for print
        body = body.replace('<details class="cor">', '<details class="cor" open>')
        out.append(f'<h1 class="ch"><span class="num">{cls}</span>{html.escape(title.split("·",1)[1].strip())}</h1>'
                   + (f'<p class="readings">{html.escape(read)}</p>' if read else '')
                   + essh + body)
    return ''.join(out)

def practice():
    out = ['<h1 class="ch"><span class="num">§</span>Practice, class by class</h1><p>Every exercise with its full statement and a step-by-step correction. "Official solution" = published by the professor; "Proposed solution" = worked with the course method while the official one is not open on Moodle.</p>']
    for e in a['exercises']:
        if not e['id'].startswith('s'): continue
        body = e['en'][1].replace('<details class="cor">', '<details class="cor" open>')
        out.append(f'<h4>{html.escape(e["title"])}</h4>{body}')
    return ''.join(out)

def mcq():
    out = ['<h1 class="ch"><span class="num">§</span>MCQ annex, with answers</h1>']
    cur = None
    titles = dict((c[0], c[1]) for c in a['chapters'])
    for q in a['qcm']:
        if q[0] != cur:
            cur = q[0]
            out.append(f'<h4>{html.escape(titles.get(cur, "Sample exam (exfa)"))}</h4>')
        opts = ''.join(f'<li>{html.escape(o)}</li>' for o in q[2])
        out.append(f'<div class="q"><div class="qq">{html.escape(q[1])}</div><ol type="a">{opts}</ol>'
                   f'<div class="ans">Answer: {html.escape(q[2][q[3]])}</div>'
                   f'<div class="ex">{html.escape(q[4]) if len(q)>4 and q[4] else ""}</div></div>')
    return ''.join(out)

def gloss():
    rows = ''.join(f'<tr><td><b>{html.escape(t)}</b></td><td>{html.escape(d)}</td></tr>' for t, d in GLOSSARY)
    return f'<h1 class="ch"><span class="num">§</span>Key terms</h1><table><tr><th>Term</th><th>Definition</th></tr>{rows}</table>'

doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Refresher Course Accounting - Revision notes</title><style>{css}</style></head><body>
{cover()}{toc()}{chapters()}{practice()}{gloss()}{mcq()}
</body></html>"""
open(f'{ROOT}/pdf/fiche-acc.html', 'w').write(doc)
print('fiche html written:', len(doc), 'chars')
