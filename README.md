# NURZING — Web App + SEO Site

A React + Vite customer web app for the NURZING nursing bureau, plus a set of static,
SEO-friendly pages (landing + service + city pages).

## Structure (deployed)

| Path | What it is |
| --- | --- |
| `/` | Static landing page (content-rich, indexed by Google) |
| `/services/*.html` | One page per service (home nursing, elderly care, …) |
| `/cities/*.html` | One page per city (Bengaluru, Mumbai, …) |
| `/app/` | The React SPA (discover, profile, booking, tracking) — `noindex` |
| `/robots.txt`, `/sitemap.xml` | Crawling + sitemap |
| `/assets/site.css` | Shared stylesheet for the static pages |

The app lives under `/app/` so the marketing/SEO pages stay at clean, crawlable URLs.
`public/_redirects` sends `/app/*` to the SPA shell for client-side routing.

## Run locally
    npm install
    npm run dev        # dev server — open http://localhost:5173/app/

(The app uses `basename="/app"`, so in dev it is served under `/app/`.)

## Build
    bash build.sh      # regenerates SEO pages, bundles the app, assembles dist/
    npm run preview    # preview a Vite build (optional)

`build.sh` uses esbuild directly (the same output the deployed `dist/` contains).
`gen_pages.py` generates the service + city pages and `sitemap.xml` from one template.

## Deploy (Cloudflare Pages)
- Build output directory: `dist`
- A **pre-built `dist/` is committed**, so the project can serve it as-is.
- `.github/workflows/deploy.yml` deploys `dist/` to Cloudflare Pages on every push to `main`
  (uses the repo secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`).

## SEO notes
- Each static page has its own `<title>`, meta description, canonical URL, Open Graph tags
  and JSON-LD structured data.
- The SPA shell is `noindex, follow` — thin JS pages shouldn't be indexed; the static pages
  are the SEO surface.
- After deploy: submit `sitemap.xml` in **Google Search Console**.

## Replace before launch
This is a demo build. Replace every placeholder with verified, real information:
- **Landing + service/city pages** — every `[placeholder]` / "Placeholder:" note, and any
  verification or insurance claim.
- **Sample professionals** (`src/data/nurses.js`) — the 12 nurses, their ratings, review
  counts and reviews are invented.
- **Contact details** — phone and email are placeholders.
- **Rates** — all prices are placeholders.

Do not publish invented testimonials or unverified claims (misleading-advertising /
consumer-protection risk in India).

## Data layer
Seed data lives in `src/data/nurses.js`; bookings and saved items are stored in the browser
(`src/lib/store.jsx`). Swap those two to move to a real backend.
