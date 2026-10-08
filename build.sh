#!/bin/bash
set -e
cd /scratch/work/nurzing-app
rm -rf dist && mkdir -p dist/assets
./node_modules/.bin/esbuild src/main.jsx --bundle --format=iife --jsx=automatic --minify \
  --define:process.env.NODE_ENV='"production"' --outfile=dist/assets/app.js --log-level=warning
python3 gen_pages.py
cp -r public/. dist/
echo "built: $(find dist -type f | wc -l) files, $(du -sh dist | cut -f1)"
