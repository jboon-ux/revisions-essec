#!/usr/bin/env python3
# Regenerates pdf/<id>-fr.pdf and pdf/<id>-en.pdf for mm, it, law, str, fin from data/<id>.json.
# Usage: python3 tools/gen-fiches.py [ROOT]   (writes /tmp/fiche-<id>-<lang>.html, then print with headless Chrome)
import json, html, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
E = html.escape
CSS = open(f'{ROOT}/tools/fiche.css').read()
L = {
 'fr': dict(k='Fiche de révision synthétique', toc='Sommaire', ev='Évaluation', ess='L\'essentiel', infos='Infos pratiques', plan='Plan du cours', ex='Exercices', exams='Examens blancs et fiches', mcq='QCM d\'entraînement', ans='Réponse', pend='Chapitres à venir (pas encore de support)', cover_note='Les chapitres reprennent les supports du cours publiés sur Moodle. Les corrections marquées « proposée » sont celles de Instinct, pas du professeur.', gen='Généré le 25 nov. 2026 à partir du site de révision.'),
 'en': dict(k='Condensed revision sheet', toc='Contents', ev='Assessment', ess='In one look', infos='Practical info', plan='Course plan', ex='Exercises', exams='Mock exams and sheets', mcq='Practice MCQs', ans='Answer', pend='Upcoming chapters (no material yet)', cover_note='Chapters follow the course material published on Moodle. Solutions marked "suggested" or "proposed" are Instinct\'s own, not the professor\'s.', gen='Generated on 25 Nov 2026 from the revision site.'),
}
def op(h): return h.replace('<details class="cor">', '<details class="cor" open>')
def build(sid, lang):
    d = json.load(open(f'{ROOT}/data/{sid}.json')); t = L[lang]
    fr = {x[0]: x[2] for x in d['fr']}; en = {x[0]: x[2] for x in d['en']}
    body = lambda cid: ((en.get(cid) if lang == 'en' else fr.get(cid)) or fr.get(cid) or en.get(cid, ''))
    ess = {x[0]: x[1] for x in d['ess']}
    qc = {}
    for q in d['qcm']: qc.setdefault(q[0], []).append(q)
    out = [f'<div class="cover"><div class="k">{E(d["code"])} · ESSEC MiM 1 · {"Automne" if lang=="fr" else "Fall"} 2026</div><h1>{E(d["name"])}</h1><h2>{t["k"]} · {E(d["prof"])}</h2><div class="meta"><b>{t["ev"]}.</b> {E(d["eval"])}</div><div class="assess">{t["cover_note"]}<br><small>{t["gen"]}</small></div></div>']
    out.append(f'<h1 class="ch"><span class="num">§</span>{t["toc"]}</h1><div class="toc">' + ''.join(f'<div><b>{i+1}.</b> {E(c[1])}</div>' for i, c in enumerate(d['chapters'])) + '</div>')
    out.append('<div class="main">')
    if d.get('pending'): out.append(f'<p class="readings"><b>{t["pend"]}:</b> ' + E(' · '.join(d['pending'])) + '</p>')
    for i, (cid, title) in enumerate(d['chapters']):
        e = ess.get(cid, [])
        eh = f'<div class="key"><b>{t["ess"]}.</b><ul>' + ''.join(f'<li>{x}</li>' for x in e) + '</ul></div>' if e else ''
        out.append(f'<h1 class="ch"><span class="num">{i+1:02d}</span>{E(title)}</h1>{eh}{op(body(cid))}')
    ex = d.get('exercises') or []
    if ex:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["ex"]}</h1>')
        for e in ex:
            h = (e.get(lang) or e.get('fr') or e.get('en'))
            out.append(f'<h4>{E(e["title"])}</h4>{op(h[1])}')
    ms = d.get('exams') or []
    if ms:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["exams"]}</h1>')
        for m in ms:
            h = m.get(lang) or m.get('fr') or m.get('en')
            out.append(f'<h4>{E(m["title"])}</h4>{op(h[1])}')
    inf = d.get('infos') or []
    ic = d.get('infoContent') or []
    if inf or ic:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["infos"]}</h1>')
        for x in inf: out.append(f'<h4>{E(x[0])}</h4><ul>' + ''.join(f'<li>{E(l)}</li>' for l in x[1]) + '</ul>')
        for x in ic:
            h = x.get(lang) or x.get('fr') or x.get('en')
            out.append(f'<h4>{E(x["title"])}</h4>{h}')
    out.append(f'<h1 class="ch"><span class="num">§</span>{t["mcq"]} ({len(d["qcm"])})</h1>')
    titles = dict(d['chapters'])
    for cid, qs in qc.items():
        out.append(f'<h4>{E(titles.get(cid, cid))}</h4>')
        for n, q in enumerate(qs, 1):
            out.append(f'<div class="q"><div class="qq">{n}. {E(q[1])}</div><ol type="a">' + ''.join(f'<li>{E(o)}</li>' for o in q[2]) + f'</ol><div class="ans">{t["ans"]}: {"abcd"[q[3]]}. {E(q[2][q[3]])}</div><div class="ex">{E(q[4]) if len(q)>4 and q[4] else ""}</div></div>')
    out.append('</div>')
    return f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{E(d["name"])}</title><style>{CSS}</style></head><body>{"".join(out)}</body></html>'
for sid in ('mm', 'it', 'law', 'str', 'fin'):
    for lang in ('fr', 'en'):
        h = build(sid, lang); open(f'/tmp/fiche-{sid}-{lang}.html', 'w').write(h); print(sid, lang, len(h))
