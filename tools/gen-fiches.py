#!/usr/bin/env python3
# Regenerates pdf/<id>-fr.pdf and pdf/<id>-en.pdf for mm, it, law, str, fin from data/<id>.json.
# Usage: python3 tools/gen-fiches.py [ROOT]   (writes /tmp/fiche-<id>-<lang>.html, then print with headless Chrome)
import json, html, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
E = html.escape
CSS = open(f'{ROOT}/tools/fiche.css').read()
L = {
 'fr': dict(k='Fiche synthèse', toc='Sommaire', ev='Évaluation', ess='L\'essentiel', infos='Infos pratiques', plan='Plan du cours', ex='Exercices', exams='Examens blancs et fiches', mcq='QCM d\'entraînement', ans='Réponse', pend='Chapitres à venir (pas encore de support)', cover_note='Les chapitres reprennent les supports du cours publiés sur Moodle. Les corrections marquées « proposée » sont celles de Instinct, pas du professeur.', gen='Généré le 25 nov. 2026 à partir du site de révision.'),
 'en': dict(k='Summary sheet', toc='Contents', ev='Assessment', ess='In one look', infos='Practical info', plan='Course plan', ex='Exercises', exams='Mock exams and sheets', mcq='Practice MCQs', ans='Answer', pend='Upcoming chapters (no material yet)', cover_note='Chapters follow the course material published on Moodle. Solutions marked "suggested" or "proposed" are Instinct\'s own, not the professor\'s.', gen='Generated on 25 Nov 2026 from the revision site.'),
}
DROP = re.compile(r"objectifs|ce que vise|outline|course plan|d'où vient|étymolog|brève histoire|citations|software is eating|origine|y2k|bug de l'an 2000|blayais|exercice de classe|azincourt|aims to do|session (learning )?(goals|objectives)|where the word|brief history|quotes to know|year 2000|class exercise", re.I)
def trim(h):
    parts = re.split(r'(?=<h4>)', h)
    return ''.join(p for p in parts if not (p.startswith('<h4>') and DROP.search(re.sub('<[^>]+>', '', p[4:p.find('</h4>')]))))
TRIV = re.compile(r"stratos|azincourt|\bcitation|est attribué|attributed to|étymolog|etymolog|kennedy|origine du mot|word .strategy. come", re.I)
KEEP = re.compile(r'<table>.*?</table>|<div class="(?:f|key|def|warn)">.*?</div>', re.S)
def synth(h):
    out = []
    for p in re.split(r'(?=<h4>)', h):
        bl = [m.group(0) for m in KEEP.finditer(p)]
        if bl:
            t = p[:p.find('</h4>') + 5] if p.startswith('<h4>') else ''
            out.append(t + ''.join(bl))
    return ''.join(out)
TT = {'Organisation du cours': 'Course organisation', 'Organisation et règles du cours': 'Course organisation and rules', 'Préparation de la séance 2': 'Session 2 preparation', 'Programme et règles du cours': 'Course programme and rules', 'Supports et préparation': 'Materials and preparation'}
def op(h): return h.replace('<details class="cor">', '<details class="cor" open>')
def build(sid, lang):
    d = json.load(open(f'{ROOT}/data/{sid}.json')); t = L[lang]
    fr = {x[0]: x[2] for x in d['fr']}; en = {x[0]: x[2] for x in d['en']}
    body = lambda cid: ((en.get(cid) if lang == 'en' else fr.get(cid)) or fr.get(cid) or en.get(cid, ''))
    ess = {x[0]: [b for b in x[1] if not TRIV.search(b)] for x in d['ess']}
    EN = json.load(open(f'{ROOT}/tools/ess-en.json')).get(sid) if lang == 'en' else None
    if EN:
        d['infos'] = EN['infos']; ess = EN['ess']; d['chapters'] = [[c, EN['title'][c]] for c, _ in d['chapters']]; d['eval'] = EN['eval']; d['pending'] = EN['pending']
    nq0 = len(d['qcm']); d['qcm'] = [q for q in d['qcm'] if not TRIV.search(q[1] + ' ' + ' '.join(q[2]) + ' ' + (q[4] if len(q) > 4 else ''))]; print(sid, lang, 'qcm dropped', nq0 - len(d['qcm']))
    qc = {}
    for q in d['qcm']: qc.setdefault(q[0], []).append(q)
    out = [f'<div class="cover"><div class="k">{E(d["code"])} · ESSEC MiM 1</div><h1>{E(d["name"])}</h1><h2>{t["k"]}</h2></div>']
    out.append(f'<h1 class="ch"><span class="num">§</span>{t["toc"]}</h1><div class="toc">' + ''.join(f'<div><b>{i+1}.</b> {E(c[1])}</div>' for i, c in enumerate(d['chapters'])) + '</div>')
    if False: out.append(f'<p class="readings"><b>{t["pend"]}:</b> ' + E(' · '.join(d['pending'])) + '</p>')
    for i, (cid, title) in enumerate(d['chapters']):
        e = ess.get(cid, [])
        eh = f'<div class="key"><b>{t["ess"]}.</b><ul>' + ''.join(f'<li>{x}</li>' for x in e) + '</ul></div>' if e else ''
        out.append(f'<h1 class="ch"><span class="num">{i+1:02d}</span>{E(title)}</h1>{eh}{op(synth(trim(body(cid))))}')
    ex = []
    if ex:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["ex"]}</h1>')
        for e in ex:
            h = (e.get(lang) or e.get('fr') or e.get('en'))
            out.append(f'<h4>{E(e["title"])}</h4>{op(h[1])}')
    ms = []
    if ms:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["exams"]}</h1>')
        for m in ms:
            h = m.get(lang) or m.get('fr') or m.get('en')
            out.append(f'<h4>{E(m["title"])}</h4>{op(h[1])}')
    inf = d.get('infos') or []
    ic = d.get('infoContent') or []
    if False:
        out.append(f'<h1 class="ch"><span class="num">§</span>{t["infos"]}</h1>')
        for x in inf: out.append(f'<h4>{E(x[0])}</h4><ul>' + ''.join(f'<li>{E(l)}</li>' for l in x[1]) + '</ul>')
        for x in ic:
            h = x.get(lang) or x.get('fr') or x.get('en')
            out.append(f'<h4>{E(TT.get(x["title"], x["title"]) if lang == "en" else x["title"])}</h4>{h}')
    return f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{E(d["name"])}</title><style>{CSS}</style></head><body>{"".join(out)}</body></html>'
for sid in ('mm', 'it', 'law', 'str', 'fin'):
    for lang in (json.load(open(f'{ROOT}/data/{sid}.json'))['lang'].lower(),):
        h = build(sid, lang); open(f'/tmp/fiche-{sid}-{lang}.html', 'w').write(h); print(sid, lang, len(h))
