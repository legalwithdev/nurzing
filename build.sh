#!/bin/bash
set -e
cd /scratch/work/nurzing-app
rm -rf dist && mkdir -p dist/assets
./node_modules/.bin/esbuild src/main.jsx --bundle --format=iife --jsx=automatic --minify \
  --define:process.env.NODE_ENV='"production"' --outfile=dist/assets/app.js --log-level=warning
cp public/favicon.svg public/_redirects public/landing.html public/robots.txt public/sitemap.xml dist/
cat > dist/index.html <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#062A28" />
    <title>NURZING — Book verified nurses at home</title>
    <meta name="description" content="NURZING — discover nurses and attendants, see transparent pricing, and book home care in minutes." />
    <link rel="canonical" href="https://nurzing.pages.dev/" />
    <meta name="robots" content="index, follow" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="NURZING — Book verified nurses at home" />
    <meta property="og:description" content="Discover nurses and attendants, see transparent pricing, and book home care in minutes." />
    <meta property="og:url" content="https://nurzing.pages.dev/" />
    <meta name="twitter:card" content="summary" />
    <link rel="icon" href="/favicon.svg" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/assets/app.css" />
  </head>
  <body>
    <div id="root"></div>
    <script defer src="/assets/app.js"></script>
  </body>
</html>
HTML
echo "built: $(find dist -type f | wc -l) files, $(du -sh dist | cut -f1)"
