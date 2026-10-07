# NURZING — Web App

A React + Vite customer web app for the NURZING nursing bureau: discover verified nurses,
view profiles and reviews, book home care with live transparent pricing, and track bookings.

## Stack
- React 18 + Vite 5
- React Router (client-side routing)
- Plain CSS design system (deep teal + warm gold)
- State in React Context, persisted to `localStorage` (no backend required to run)

## Run locally
    npm install
    npm run dev        # http://localhost:5173

## Build
    npm run build      # outputs to dist/
    npm run preview    # preview the production build

## Deploy (Cloudflare Pages)
This repo is ready for Cloudflare Pages:
- Build command: `npm run build`
- Build output directory: `dist`
- `public/_redirects` already routes all paths to `/index.html` for SPA routing.
- `wrangler.toml` is included (`pages_build_output_dir = "dist"`).
- A **pre-built `dist/` is committed** as a fallback: if you don't want a build step, set the Build output
  directory to `dist` and the committed output will be served as-is.

## Screens
- **Discover** (`/`) — search + filters (care type, city, sort) and nurse cards
- **Profile** (`/nurse/:id`) — verification badges, stats, skills, reviews
- **Booking** (`/book/:id`) — 3-step flow with a live price estimate
- **Bookings** (`/bookings`) — status timeline with demo "advance status"
- **Saved** (`/saved`) — shortlisted professionals
- **Account** (`/account`) — profile and preferences

## Replace before launch
This is a demo build. Before going live, replace the placeholder content with verified, real information:
- **Landing page** (`public/landing.html`) — every bracketed `[placeholder]`, and any verification / insurance claim.
- **Sample professionals** (`src/data/nurses.js`) — the 12 nurses, their ratings, review counts and reviews are invented.
- **Verification badges** on profiles — only show checks you genuinely perform.
- **Contact details** — phone and email are placeholders.

Do not publish invented testimonials or unverified claims (misleading-advertising / consumer-protection risk in India).

## Data layer
Seed data lives in `src/data/nurses.js`. Bookings and saved items are stored in the browser.
To move to a real backend (e.g. a Cloudflare Worker + D1/KV), swap the functions in
`src/lib/store.jsx` and the seed import — the UI reads everything through that layer.

> Note: `index.html` at the repo root is the Vite entry for this app.
> The earlier marketing landing page is preserved at `landing.html`.
