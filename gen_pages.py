#!/usr/bin/env python3
"""Generate static SEO pages (services + cities) and sitemap.xml into public/."""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, 'public')
BASE = 'https://nurzing.pages.dev'

SERVICES = [
    ('home-nursing', 'Home Nursing', 'Skilled nursing care at home',
     'Professional nursing care at home for medication management, wound care, injections and monitoring — for recovery, chronic conditions and long-term support.',
     ['Medication management and reminders', 'Wound dressing and post-operative care',
      'Injections, IV infusions and nebulisation', 'Vitals monitoring and doctor coordination',
      'Catheter and tube care', 'Family guidance on day-to-day care']),
    ('elderly-care', 'Elderly Care', 'Elderly care and attendants at home',
     'Daily-living support and companionship for seniors — mobility, hygiene, feeding and safety supervision at home.',
     ['Mobility and transfer support', 'Bathing, grooming and hygiene', 'Feeding and nutrition support',
      'Companionship and engagement', 'Fall prevention and safety', 'Medicine reminders']),
    ('post-surgical-care', 'Post-Surgical Care', 'Post-surgical recovery care at home',
     'Structured recovery support after surgery — dressing, drain care, pain monitoring and coordination with your doctor and physiotherapist.',
     ['Dressing and drain care', 'Pain and vitals monitoring', 'Post-operative mobility support',
      'Physiotherapy coordination', 'Nutrition and recovery guidance']),
    ('mother-baby-care', 'Mother & Baby Care', 'Mother and baby care at home',
     'Support for new mothers and newborns — feeding, newborn hygiene, sleep routines and post-partum care.',
     ['Newborn care and hygiene', 'Feeding and lactation support', 'Sleep routine help',
      'Post-partum care for the mother', 'Day and night shifts']),
    ('physiotherapy', 'Physiotherapy at Home', 'Physiotherapy at home',
     'Physiotherapy for post-surgery rehabilitation, stroke recovery, pain management and mobility at home.',
     ['Post-surgery rehabilitation', 'Stroke and neuro rehabilitation', 'Pain management',
      'Mobility and strength training', 'Structured progress plans']),
    ('icu-nursing', 'ICU-Trained Nursing', 'ICU-trained nursing at home',
     'Critical-care trained nursing support at home for complex cases requiring close monitoring.',
     ['Ventilator and respiratory support', 'Tracheostomy care', 'Catheter and tube management',
      'Continuous monitoring', 'Emergency-ready nursing cover']),
]

CITIES = ['Bengaluru', 'Mumbai', 'Delhi NCR', 'Pune', 'Hyderabad', 'Chennai']
CITY_SLUG = {'Bengaluru': 'bengaluru', 'Mumbai': 'mumbai', 'Delhi NCR': 'delhi-ncr',
             'Pune': 'pune', 'Hyderabad': 'hyderabad', 'Chennai': 'chennai'}

PAGE_CSS = """
.pnav{position:sticky;top:0;z-index:50;background:rgba(251,248,241,.9);backdrop-filter:blur(14px);border-bottom:1px solid var(--line-2)}
.pnav .in{max-width:900px;margin:0 auto;padding:14px 22px;display:flex;align-items:center;gap:18px}
.pnav a{font-size:.9rem;font-weight:500;color:var(--teal-900);opacity:.85}
.pnav a:hover{opacity:1;color:var(--teal-600)}
.pnav .sp{margin-left:auto}
.pwrap{max-width:820px;margin:0 auto;padding:44px 22px 90px}
.crumbs{font-size:.8rem;color:var(--muted);margin-bottom:18px}
.crumbs a{color:var(--teal-700)}
.pwrap h1{font-size:clamp(1.9rem,4vw,2.9rem);color:var(--teal-1000);margin-bottom:.7rem}
.pwrap .lead{font-size:1.08rem;color:var(--muted);margin-bottom:2rem;max-width:42rem}
.pwrap h2{font-size:1.5rem;color:var(--teal-1000);margin:2.4rem 0 .8rem}
.pwrap p{color:#33413f;margin-bottom:.9rem}
.pwrap ul{margin:.4rem 0 1rem 0;padding:0;list-style:none;display:grid;gap:.6rem}
.pwrap ul li{display:flex;gap:.6rem;align-items:flex-start;color:#33413f}
.pwrap ul li::before{content:"";flex:0 0 7px;width:7px;height:7px;border-radius:50%;background:var(--gold-500);margin-top:.55rem}
.note{background:rgba(217,183,97,.14);border:1px solid rgba(198,156,66,.35);border-radius:14px;padding:14px 16px;font-size:.86rem;color:var(--teal-900);margin:1.6rem 0}
.pcta{background:linear-gradient(150deg,var(--teal-900),var(--teal-1000));color:var(--cream);border-radius:24px;padding:34px 28px;text-align:center;margin:2.6rem 0}
.pcta h2{color:var(--cream);margin:0 0 .6rem}
.pcta p{color:var(--teal-200);margin-bottom:1.4rem}
.chiprow{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0 0}
.chiprow a{font-size:.82rem;font-weight:600;color:var(--teal-800);background:rgba(10,64,60,.06);border:1px solid var(--line);padding:.5rem .8rem;border-radius:999px}
.chiprow a:hover{background:var(--teal-950);color:var(--gold-300);border-color:var(--teal-950)}
.pfoot{border-top:1px solid var(--line);margin-top:40px;padding-top:24px;font-size:.82rem;color:var(--muted)}
"""

def head(title, desc, path, ld=None):
    ldjson = ''
    if ld:
        ldjson = '\n<script type="application/ld+json">%s</script>' % ld
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8" />\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            '<title>%s</title>\n<meta name="description" content="%s" />\n'
            '<link rel="canonical" href="%s%s" />\n<meta name="robots" content="index, follow" />\n'
            '<meta property="og:type" content="website" />\n<meta property="og:title" content="%s" />\n'
            '<meta property="og:description" content="%s" />\n<meta property="og:url" content="%s%s" />\n'
            '<meta name="twitter:card" content="summary" />\n'
            '<link rel="icon" href="/favicon.svg" />\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />\n'
            '<link rel="stylesheet" href="/assets/site.css" />\n<style>%s</style>%s\n</head>\n'
            % (title, desc, BASE, path, title, desc, BASE, path, PAGE_CSS, ldjson))

NAV = ('<header class="pnav"><div class="in">'
       '<a href="/"><b>NURZING</b></a>'
       '<a href="/services/home-nursing.html">Services</a>'
       '<a href="/cities/bengaluru.html">Cities</a>'
       '<a class="sp" href="/app/">Open app</a>'
       '</div></header>')

def foot(city_or_service_links):
    return ('<footer class="pfoot">NURZING is a nursing bureau and placement service. '
            'Indicative information only — final rates and availability are confirmed by a care advisor. '
            'In a medical emergency, call your local emergency number.<br/><br/>'
            '%s</footer>' % city_or_service_links)

def write(path, html):
    full = os.path.join(PUB, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, 'w', encoding='utf-8').write(html)

urls = ['/']

# ---------------- service pages ----------------
for slug, name, h1, lead, items in SERVICES:
    path = '/services/%s.html' % slug
    title = '%s \u2014 %s at Home | NURZING' % (h1, name)
    desc = lead[:150]
    citylinks = ''.join('<a href="/cities/%s.html">%s</a>' % (CITY_SLUG[c], c) for c in CITIES)
    other = ''.join('<a href="/services/%s.html">%s</a>' % (s[0], s[1]) for s in SERVICES if s[0] != slug)
    ld = ('{"@context":"https://schema.org","@type":"Service","name":"%s","serviceType":"%s",'
          '"provider":{"@type":"MedicalBusiness","name":"NURZING","url":"%s/"},'
          '"areaServed":"India","url":"%s%s"}' % (name, name, BASE, BASE, path))
    html = (head(title, desc, path, ld) + '<body>' + NAV + '<main class="pwrap">'
            + '<div class="crumbs"><a href="/">Home</a> &rsaquo; <a href="/services/home-nursing.html">Services</a> &rsaquo; %s</div>' % name
            + '<h1>%s</h1>' % h1
            + '<p class="lead">%s</p>' % lead
            + '<h2>What\'s included</h2><ul>' + ''.join('<li>%s</li>' % i for i in items) + '</ul>'
            + '<h2>Who it\'s for</h2><p>Families who need dependable care at home — after a hospital stay, for a chronic condition, for an ageing parent, or for ongoing support. Care can be arranged for a single shift or for longer, live-in cover.</p>'
            + '<h2>How it works</h2><p>Tell us the care type, shift and location. We match you with a suitable professional and confirm the details with you before care begins.</p>'
            + '<div class="note">Placeholder: add your real rates, verification details and availability for %s before launch. Do not publish claims you cannot substantiate.</div>' % name
            + '<h2>Available in</h2><div class="chiprow">' + citylinks + '</div>'
            + '<div class="pcta"><h2>Book %s</h2><p>See matched professionals and a transparent price range in the app.</p><a class="btn btn-gold btn-lg" href="/app/">Open the app &rarr;</a></div>'
            + '<h2>Other services</h2><div class="chiprow">' + other + '</div>'
            + '</main>' + foot('<a href="/">NURZING home</a>') + '</body></html>')
    write(path.lstrip('/'), html)
    urls.append(path)

# ---------------- city pages ----------------
for city in CITIES:
    slug = CITY_SLUG[city]
    path = '/cities/%s.html' % slug
    title = 'Home Nursing & Patient Attendants in %s | NURZING' % city
    desc = ('Arrange home nursing, elderly care, post-surgical care, mother and baby care, physiotherapy '
            'and trained attendants in %s.' % city)
    svclinks = ''.join('<a href="/services/%s.html">%s</a>' % (s[0], s[1]) for s in SERVICES)
    citylinks = ''.join('<a href="/cities/%s.html">%s</a>' % (CITY_SLUG[c], c) for c in CITIES if c != city)
    ld = ('{"@context":"https://schema.org","@type":"Service","name":"Home nursing in %s","areaServed":"%s",'
          '"provider":{"@type":"MedicalBusiness","name":"NURZING","url":"%s/"},"url":"%s%s"}'
          % (city, city, BASE, BASE, path))
    html = (head(title, desc, path, ld) + '<body>' + NAV + '<main class="pwrap">'
            + '<div class="crumbs"><a href="/">Home</a> &rsaquo; <a href="/cities/bengaluru.html">Cities</a> &rsaquo; %s</div>' % city
            + '<h1>Home nursing and attendants in %s</h1>' % city
            + '<p class="lead">Arrange nursing, attendants and recovery care at home in %s. Tell us the care type, shift and location, and we confirm the details with you before care begins.</p>' % city
            + '<h2>Services in %s</h2><div class="chiprow">' % city + svclinks + '</div>'
            + '<h2>Shifts and duration</h2><p>Care can be arranged for 12-hour day or night shifts, 24-hour live-in cover, or short visits — depending on the need.</p>'
            + '<h2>How it works</h2><p>Share the care type, shift and your area. We match you with a suitable professional and confirm the plan with you before anything begins.</p>'
            + '<div class="note">Placeholder: add the exact areas you cover in %s, your real rates, and your local contact details before launch.</div>' % city
            + '<div class="pcta"><h2>Book care in %s</h2><p>See matched professionals and a transparent price range in the app.</p><a class="btn btn-gold btn-lg" href="/app/">Open the app &rarr;</a></div>'
            + '<h2>Other cities</h2><div class="chiprow">' + citylinks + '</div>'
            + '</main>' + foot('<a href="/">NURZING home</a>') + '</body></html>')
    write(path.lstrip('/'), html)
    urls.append(path)

# ---------------- sitemap ----------------
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    pri = '1.0' if u == '/' else '0.8'
    sm.append('  <url><loc>%s%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>' % (BASE, u, pri))
sm.append('</urlset>')
io.open(os.path.join(PUB, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')

print('generated: %d service pages, %d city pages, sitemap with %d urls'
      % (len(SERVICES), len(CITIES), len(urls)))
