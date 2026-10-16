#!/usr/bin/env python3
"""Sync the landing page's nurse feed with src/data/nurses.js (single source of truth).

The card MUST show each professional's own designation (their `role` exactly as
listed) — never a hardcoded or mapped label such as "RN". Registration is a
SEPARATE field (`regType` / `regVerified`) and may only be shown as a badge when
`regVerified` is true. Run this after editing src/data/nurses.js so the landing
and the app can never disagree.
"""
import io, os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
LANDING = os.path.join(HERE, 'public', 'index.html')
DATA = os.path.join(HERE, 'src', 'data', 'nurses.js')

src = io.open(DATA, encoding='utf-8').read()

pat = re.compile(
    r"\{ id: '(nz-\d+)', tier: (\d+), regType: '([^']+)', regVerified: (true|false), qual: '([^']*)', "
    r"name: '([^']+)', role: '([^']+)', city: '([^']+)', area: '([^']+)', "
    r"rate: (\d+), rating: ([\d.]+), reviews: (\d+), years: (\d+), availableToday: (true|false), "
    r"distanceKm: ([\d.]+),\s*\n\s*careTypes: \[([^\]]+)\]"
)

items = []
for m in pat.finditer(src):
    (gid, tier, regtype, regv, qual, name, role, city, area,
     rate, rating, reviews, years, av, km, ct) = m.groups()
    care = [x.strip().strip("'") for x in ct.split(',')]
    # `r` is the professional's OWN designation, copied verbatim. No mapping, no suffixes.
    # `regt` / `regv` are the registration type and its verified flag — separate from `r`.
    items.append((int(tier), '{n:%s,r:%s,ql:%s,regt:%s,regv:%s,c:%s,a:%s,rate:%d,rt:%.1f,rev:%d,y:%d,av:%s,km:%s,ct:%s}' % (
        json.dumps(name), json.dumps(role), json.dumps(qual), json.dumps(regtype),
        'true' if regv == 'true' else 'false',
        json.dumps(city), json.dumps(area), int(rate), float(rating),
        int(reviews), int(years), 'true' if av == 'true' else 'false',
        km, json.dumps(care))))

if not items:
    raise SystemExit('sync_nurses: parsed 0 nurses from %s — aborting' % DATA)

items.sort(key=lambda t: t[0])          # tier first: licensed RN&RM / B.Sc nurses on top
array = ("  /* GENERATED from src/data/nurses.js by sync_nurses.py — do not hand-edit.\n"
         "     `r` = the professional's own designation, shown verbatim.\n"
         "     `regt`/`regv` = registration type + verified flag (badge only when true).\n"
         "     Ordered by tier: licensed RN&RM / B.Sc nurses first. */\n"
         "  var NURSES = [" + ','.join(x[1] for x in items) + '];')

html = io.open(LANDING, encoding='utf-8').read()
new, n = re.subn(r'\n(?:  /\* GENERATED[^\n]*\n(?:     [^\n]*\n)*)?  var NURSES = \[.*?\];',
                 lambda m: '\n' + array, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('sync_nurses: could not find the NURSES block in the landing')
io.open(LANDING, 'w', encoding='utf-8').write(new)
print('sync_nurses: wrote %d professionals into the landing feed' % len(items))
