#!/usr/bin/env python3
"""Generate one page per landing section (everything except the nurse-card feed).

Each page carries the FULL content of its section, the site header/footer, and only
the JS that page needs. URLs are appended to sitemap.xml.
"""
import io, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, 'public')
BASE = 'https://nurzing.pages.dev'
TODAY = datetime.date.today().isoformat()

SECTIONS = [
    ('licensed-care',  'LICENSED TIER',      'Licensed Home Nursing Care \u2014 What RN&amp;RM Means | NURZING',
     'What RN&amp;RM registration, B.Sc Nursing, experience and a specialisation actually mean \u2014 and why not every caregiver is a nurse.'),
    ('services',       'SERVICES',           'Home Nursing &amp; Care Services \u2014 What We Arrange | NURZING',
     'Every kind of care NURZING arranges: home nursing, live-in, elderly care, post-surgical, mother &amp; baby, physiotherapy and ICU-trained nurses.'),
    ('book',           'MATCH / BOOKING',    'Book a Nurse or Attendant at Home | NURZING',
     'Get a care match in under a minute \u2014 pick the care type, shift and area, and see an indicative price range before you commit.'),
    ('how-it-works',   'HOW',                'How NURZING Works | NURZING',
     'How arranging care at home works with NURZING \u2014 from your request to a confirmed professional.'),
    ('why-nurzing',    'WHY',                'Why Families Choose NURZING | NURZING',
     'What makes NURZING different \u2014 licensed nurses shown first, transparent pricing and a real care advisor.'),
    ('numbers',        'STATS',              'NURZING by the Numbers | NURZING',
     'NURZING in numbers \u2014 professionals, care shifts and family rating. Placeholder figures for the demo build.'),
    ('reviews',        'TESTIMONIALS',       'Family Reviews | NURZING',
     'What families say about NURZING. Demo placeholders \u2014 real reviews are published only with consent.'),
    ('faq',            'FAQ',                'Home Nursing \u2014 Frequently Asked Questions | NURZING',
     'Plain answers to the questions families ask before arranging nursing or attendant care at home.'),
]

ANCHOR_MAP = {
    '#tier': '/licensed-care.html', '#services': '/services.html', '#match': '/book.html',
    '#how': '/how-it-works.html', '#why': '/why-nurzing.html', '#stats': '/numbers.html',
    '#reviews': '/reviews.html', '#faq': '/faq.html', '#top': '/',
}

src = io.open(os.path.join(PUB, 'index.html'), encoding='utf-8').read()
# Section content lives in its own source file so the landing can stay focused.
SEC_SRC = io.open(os.path.join(HERE, 'sections_source.html'), encoding='utf-8').read()

def between(a, b):
    i = src.index(a); j = src.index(b)
    return src[i:j]

BOOT = src[src.index('<script>(function(){try{var t=localStorage'):src.index('</script>', src.index('<script>(function(){try{var t=localStorage')) + 9]
BANNER = between('<div class="demo-banner">', '</div>') + '</div>'
HEADER = between('<header id="hdr">', '</header>') + '</header>'
FOOTER = between('<footer>', '</footer>') + '</footer>'

# the landing's own nav (desktop + mobile) — reuse on the section pages
i = src.index('<div class="mobile-menu"'); MOBILEMENU = src[i:src.index('<main id="top">')].strip()

# main script (block before the nurse-feed script)
s1 = src.index('<script>', src.index('<!-- APP DOCK'))
s2 = src.index('</script>', s1)
MAINJS = src[s1 + len('<script>'):s2]

MARK = re.compile(r'/\* -+ ([^-]+?) -+ \*/')
blocks = {}
marks = list(MARK.finditer(MAINJS))
for k, m in enumerate(marks):
    end = marks[k + 1].start() if k + 1 < len(marks) else len(MAINJS)
    blocks[m.group(1).strip()] = MAINJS[m.end():end].strip()

COMMON_JS = '\n'.join(x for x in [blocks.get('nav',''), blocks.get('theme (manual)',''), blocks.get('reveal','')] if x)

# on /book.html, read ?n= &r= &c= and pre-select the professional's care type
BOOK_JS = """
(function(){
  var p = new URLSearchParams(location.search);
  var nm = p.get('n'), rl = p.get('r'), cr = p.get('c');
  if(!nm && !cr) return;
  var box = document.getElementById('matcherNurse');
  if(box && nm){ box.hidden = false; box.innerHTML = 'Booking with <b>' + nm + '</b>' + (rl ? '<span class="mn-r">' + rl + '</span>' : ''); }
  var MAP = {'Home Nursing':'Home Nursing','ICU-trained':'ICU-Trained Nurses','Post-Surgical':'Post-Surgical Recovery',
             'Mother & Baby':'Mother & Baby Care','Elderly Care':'Elderly Care & Attendants','Physiotherapy':'Physiotherapy at Home'};
  var want = MAP[cr] || cr;
  var opts = document.querySelectorAll('#careOpts .opt');
  for(var i=0;i<opts.length;i++){ if(opts[i].textContent.trim() === want){ opts[i].click(); break; } }
})();
"""

NEEDS = {
    'services':     ['data', 'services render'],
    'book':         ['data', 'matcher'],
    'faq':          ['faq'],
}

def page(slug, title, desc, section_html, extra_js):
    path = '/%s.html' % slug
    body = section_html
    # rewrite in-page anchors to real pages
    for a, b in ANCHOR_MAP.items():
        body = body.replace('href="%s"' % a, 'href="%s"' % b)
    js = ('<script>\n' + ('\n'.join(extra_js) + '\n' if extra_js else '') + COMMON_JS + '\n</script>') if (extra_js or COMMON_JS) else ''
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%s</title>
<meta name="description" content="%s" />
<link rel="canonical" href="%s%s" />
<meta name="robots" content="index, follow" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="NURZING" />
<meta property="og:locale" content="en_IN" />
<meta property="og:title" content="%s" />
<meta property="og:description" content="%s" />
<meta property="og:url" content="%s%s" />
<meta property="og:image" content="%s/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="%s" />
<meta name="twitter:description" content="%s" />
<meta name="twitter:image" content="%s/og-image.png" />
<link rel="icon" href="/favicon.svg" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/site.css" />
<style>main#top{padding-top:92px}@media(max-width:700px){main#top{padding-top:86px}}</style>
%s
</head>
<body>
%s
%s
%s
<main id="top">
%s
</main>
%s
%s
</body>
</html>
""" % (title, desc, BASE, path, title, desc, BASE, path, BASE, title, desc, BASE, BOOT,
       BANNER, HEADER, MOBILEMENU, body, FOOTER, js)

urls = []
for slug, marker, title, desc in SECTIONS:
    i = SEC_SRC.index('<!-- %s -->' % marker)
    nxt = re.search(r'\n<!-- (?:LICENSED TIER|SERVICES|MATCH / BOOKING|HOW|WHY|STATS|TESTIMONIALS|FAQ)',
                    SEC_SRC[i + 5:])
    j = i + 5 + nxt.start() if nxt else len(SEC_SRC)
    section_html = SEC_SRC[i:j].strip()
    extra = [blocks[b] for b in NEEDS.get(slug, []) if b in blocks]
    if slug == 'book': extra = extra + [BOOK_JS]
    out = page(slug, title, desc, section_html, extra)
    io.open(os.path.join(PUB, slug + '.html'), 'w', encoding='utf-8').write(out)
    urls.append('/%s.html' % slug)
    print('wrote %s.html (%d chars, js blocks: %s)' % (slug, len(out), ','.join(NEEDS.get(slug, [])) or 'common only'))

# ---- append to sitemap ----
sp = os.path.join(PUB, 'sitemap.xml')
s = io.open(sp, encoding='utf-8').read()
add = ''.join('  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
              % (BASE, u, TODAY) for u in urls if ('%s%s' % (BASE, u)) not in s)
s = s.replace('</urlset>', add + '</urlset>')
io.open(sp, 'w', encoding='utf-8').write(s)
print('sitemap now has %d urls' % s.count('<loc>'))
