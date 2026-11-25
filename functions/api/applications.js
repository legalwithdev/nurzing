// POST /api/applications            -> a professional lists themselves (public)
// GET  /api/applications?key=...    -> admin list
// PUT  /api/applications?key=...    -> admin sets the verification checklist
import { json, bad, clean, digits, reference, throttled, ipOf, img } from './_lib.js';

// The staff and admin apps live on their own subdomains, so the browser makes a
// cross-origin request. Without these headers the admin console only shows
// "Could not reach the server".
const ORIGINS = [
  'https://nurzing.pages.dev',
  'https://nurzingstaff.pages.dev',
  'https://nurzingadmin.pages.dev',
];

function corsHeaders(request) {
  const origin = request.headers.get('origin') || '';
  const h = {
    'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'access-control-allow-headers': 'content-type',
    'access-control-max-age': '86400',
    vary: 'origin',
  };
  if (ORIGINS.includes(origin)) h['access-control-allow-origin'] = origin;
  return h;
}

function withCors(res, request) {
  const h = new Headers(res.headers);
  for (const [k, v] of Object.entries(corsHeaders(request))) h.set(k, v);
  return new Response(res.body, { status: res.status, headers: h });
}

export function onRequestOptions({ request }) {
  return new Response(null, { status: 204, headers: corsHeaders(request) });
}

const REG_TYPES = new Set(['RN&RM', 'RANM', 'none']);
const CHECKS = ['docs_ok', 'council_ok', 'education_ok', 'pcc_ok', 'physical_ok'];

async function postImpl({ request, env }) {
  let body;
  try { body = await request.json(); } catch { return bad('Invalid JSON body'); }
  if (body.company) return bad('Rejected');
  if (throttled('a:' + ipOf(request), 6)) return bad('Too many requests, try again shortly', 429);

  const name = clean(body.name, 120);
  const phone = digits(body.phone);
  const designation = clean(body.designation, 120);
  if (name.length < 2) return bad('Please enter your name');
  if (phone.length < 8) return bad('Please enter a valid phone number');
  if (designation.length < 2) return bad('Please enter your designation exactly as you want it shown');

  // Accept a typed registration type too, not only the three presets.
  const regType = REG_TYPES.has(body.reg_type) ? body.reg_type : (clean(body.reg_type, 40) || 'none');
  const ref = reference('NZA');

  if (!env.DB) return json({ ok: true, reference: ref, stored: false,
    note: 'Storage is not configured yet — please message us on WhatsApp.' });

  try {
    // Anyone can create a profile. Asking for verification is a separate choice:
    //   wants_verification = 1 -> status 'pending'  (queued for the offline check)
    //   wants_verification = 0 -> status 'profile'  (digital profile only for now)
    const wants = body.wants_verification ? 1 : 0;
    const status = wants ? 'pending' : 'profile';

    await env.DB.prepare(
      `INSERT INTO applications (reference, name, phone, designation, qualification, reg_type,
                                 reg_number, years, city, area, care_types, notes,
                                 wants_verification, status, gender, photo_url, photo_thumb,
                                 languages, shifts)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(ref, name, phone, designation, clean(body.qualification, 60), regType,
           clean(body.reg_number, 40), Math.min(60, Math.max(0, parseInt(body.years, 10) || 0)),
           clean(body.city, 80), clean(body.area, 80),
           JSON.stringify(Array.isArray(body.care_types) ? body.care_types.slice(0, 8) : []),
           clean(body.notes, 500), wants, status, clean(body.gender, 20),
           img(body.photo_url, 47000), img(body.photo_thumb, 12000),
           JSON.stringify(Array.isArray(body.languages) ? body.languages.slice(0, 12) : []),
           JSON.stringify(Array.isArray(body.shifts) ? body.shifts.slice(0, 8) : [])).run();
  } catch {
    return json({ ok: true, reference: ref, stored: false,
      note: 'We could not save it just now — please message us on WhatsApp.' });
  }
  return json({ ok: true, reference: ref, stored: true,
    wants_verification: !!body.wants_verification,
    status: body.wants_verification ? 'pending' : 'profile' });
}

async function getImpl({ request, env }) {
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || (url.searchParams.get('key') || '') !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);

  const status = url.searchParams.get('status');
  const stmt = status
    ? env.DB.prepare('SELECT * FROM applications WHERE status = ? ORDER BY id DESC LIMIT 200').bind(status)
    : env.DB.prepare('SELECT * FROM applications ORDER BY id DESC LIMIT 200');
  const { results } = await stmt.all();
  return json({ ok: true, count: results.length, applications: results });
}

// The admin sets the checklist. Status is DERIVED from it — an admin cannot
// simply mark someone verified; every mandatory check has to pass first.
async function putImpl({ request, env }) {
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || (url.searchParams.get('key') || '') !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);

  let body;
  try { body = await request.json(); } catch { return bad('Invalid JSON body'); }

  const id = parseInt(body.id, 10);
  if (!id) return bad('id is required');

  if (body.action === 'hide') {
    await env.DB.prepare(
      `UPDATE applications SET status='hidden', verified_at=NULL, verified_by=NULL,
         rejected_note=? WHERE id=?`
    ).bind(clean(body.note, 300) || 'hidden by admin', id).run();
    return json({ ok: true, id, status: 'hidden' });
  }

  if (body.action === 'unhide') {
    // Back to a plain digital profile. If they were verified before, the five
    // checks have to be done again — we do not restore a badge we cannot stand behind.
    await env.DB.prepare(
      `UPDATE applications SET status='profile', rejected_note=NULL WHERE id=?`
    ).bind(id).run();
    return json({ ok: true, id, status: 'profile' });
  }

  if (body.action === 'reject') {
    await env.DB.prepare(
      `UPDATE applications SET status='rejected', rejected_note=?, verified_at=NULL, verified_by=?
       WHERE id=?`
    ).bind(clean(body.note, 300), 'admin', id).run();
    return json({ ok: true, id, status: 'rejected' });
  }

  const checks = body.checks || {};
  const vals = CHECKS.map((c) => (checks[c] ? 1 : 0));
  const allPassed = vals.every((v) => v === 1);
  const status = allPassed ? 'verified' : 'pending';

  await env.DB.prepare(
    `UPDATE applications SET docs_ok=?, council_ok=?, education_ok=?, pcc_ok=?, physical_ok=?,
       status=?, verified_at=CASE WHEN ?='verified' THEN datetime('now') ELSE NULL END,
       verified_by=CASE WHEN ?='verified' THEN 'admin' ELSE NULL END,
       rejected_note=NULL
     WHERE id=?`
  ).bind(...vals, status, status, status, id).run();

  return json({ ok: true, id, status, checks: Object.fromEntries(CHECKS.map((c, i) => [c, vals[i]])) });
}



// DELETE /api/applications?id=..&key=..  -> permanently erase a profile.
// Irreversible: the row is removed, not flagged. A receipt is kept in
// deleted_profiles so we can still answer "what was removed and when".
async function delImpl({ request, env }) {
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || (url.searchParams.get('key') || '') !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);

  const id = parseInt(url.searchParams.get('id'), 10);
  if (!id) return bad('id is required');

  const { results } = await env.DB.prepare(
    'SELECT id, reference, name, designation, status FROM applications WHERE id = ?'
  ).bind(id).all();
  const found = results && results[0];
  if (!found) return bad('Not found', 404);

  try {
    await env.DB.prepare(
      `INSERT INTO deleted_profiles (reference, name, designation, status_before, reason)
       VALUES (?,?,?,?,?)`
    ).bind(found.reference || '', found.name || '', found.designation || '',
           found.status || '', clean(url.searchParams.get('reason'), 200) || 'admin').run();
  } catch (err) {
    // never block the delete on the audit write
  }

  await env.DB.prepare('DELETE FROM applications WHERE id = ?').bind(id).run();
  return json({ ok: true, id, reference: found.reference, name: found.name, deleted: true });
}

// ---- CORS-wrapped exports ----
export const onRequestPost = async (ctx) => withCors(await postImpl(ctx), ctx.request);
export const onRequestGet  = async (ctx) => withCors(await getImpl(ctx), ctx.request);
export const onRequestPut  = async (ctx) => withCors(await putImpl(ctx), ctx.request);
export const onRequestDelete = async (ctx) => withCors(await delImpl(ctx), ctx.request);
