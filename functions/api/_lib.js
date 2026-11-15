// Shared helpers for the NURZING Pages Functions (free tier friendly: no deps).
export const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

export const bad = (message, status = 400, extra = {}) => json({ ok: false, error: message, ...extra }, status);

export const digits = (s) => String(s || '').replace(/[^\d+]/g, '');

export const clean = (s, max = 300) =>
  String(s == null ? '' : s).replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max);

export function reference(prefix = 'NZ') {
  const t = Date.now().toString(36).toUpperCase().slice(-5);
  const r = Math.random().toString(36).toUpperCase().slice(2, 5);
  return `${prefix}-${t}${r}`;
}

// best-effort per-isolate throttle (Cloudflare gives no shared memory on the free plan)
const hits = new Map();
export function throttled(key, limit = 12, windowMs = 60_000) {
  const now = Date.now();
  const arr = (hits.get(key) || []).filter((t) => now - t < windowMs);
  if (arr.length >= limit) return true;
  arr.push(now);
  hits.set(key, arr);
  if (hits.size > 5000) hits.clear();
  return false;
}

export const ipOf = (request) =>
  request.headers.get('cf-connecting-ip') ||
  (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() ||
  'unknown';

export function whatsappLink(number, lines) {
  const n = digits(number).replace(/^\+/, '');
  const text = encodeURIComponent(lines.filter(Boolean).join('\n'));
  return n ? `https://wa.me/${n} : '';
}
