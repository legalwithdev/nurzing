// POST /api/applications            -> a professional lists themselves (public)
// GET  /api/applications?key=...    -> admin list
// PUT  /api/applications?key=...    -> admin sets the verification checklist
import { json, bad, clean, digits, reference, throttled, ipOf } from './_lib.js';

const REG_TYPES = new Set(['RN&RM', 'RANM', 'none']);
const CHECKS = ['docs_ok', 'council_ok', 'education_ok', 'pcc_ok', 'physical_ok'];

export async function onRequestPost({ request, env }) {
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

  const regType = REG_TYPES.has(body.reg_type) ? body.reg_type : 'none';
  const ref = reference('NZA');

  if (!env.DB) return json({ ok: true, reference: ref, stored: false,
    note: 'Storage is not configured yet — please message us on WhatsApp.' });

  try {
    await env.DB.prepare(
      `INSERT INTO applications (reference, name, phone, designation, qualification, reg_type,
                                 reg_number, years, city, area, care_types, notes)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(ref, name, phone, designation, clean(body.qualification, 60), regType,
           clean(body.reg_number, 40), Math.min(60, Math.max(0, parseInt(body.years, 10) || 0)),
           clean(body.city, 80), clean(body.area, 80),
           JSON.stringify(Array.isArray(body.care_types) ? body.care_types.slice(0, 8) : []),
           clean(body.notes, 500)).run();
  } catch {
    return json({ ok: true, reference: ref, stored: false,
      note: 'We could not save it just now — please message us on WhatsApp.' });
  }
  return json({ ok: true, reference: ref, stored: true });
}

export async function onRequestGet({ request, env }) {
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
export async function onRequestPut({ request, env }) {
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || (url.searchParams.get('key') || '') !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);

  let body;
  try { body = await request.json(); } catch { return bad('Invalid JSON body'); }

  const id = parseInt(body.id, 10);
  if (!id) return bad('id is required');

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
