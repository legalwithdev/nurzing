// POST /api/applications -> a professional lists themselves
import { json, bad, clean, digits, reference, throttled, ipOf } from './_lib.js';

const REG_TYPES = new Set(['RN&RM', 'RANM', 'none']);

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
  const { results } = await env.DB.prepare('SELECT * FROM applications ORDER BY id DESC LIMIT 200').all();
  return json({ ok: true, count: results.length, applications: results });
}
