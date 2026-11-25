// POST /api/bookings  -> store a care request in D1
// GET  /api/bookings?key=...  -> admin list
import { json, bad, clean, digits, reference, throttled, ipOf, whatsappLink } from '../_lib.js';

const CARE = new Set([
  'Home Nursing', 'Live-in Nursing (24x7)', 'Elderly Care & Attendants',
  'Post-Surgical Recovery', 'Mother & Baby Care', 'Physiotherapy at Home', 'ICU-Trained Nurses',
]);

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return bad('Invalid JSON body');
  }

  if (body.company) return bad('Rejected');                       // honeypot
  if (throttled('b:' + ipOf(request))) return bad('Too many requests, try again shortly', 429);

  const phone = digits(body.phone);
  if (phone.length < 8) return bad('Please enter a valid phone number');
  const care = clean(body.care_type, 60);
  if (!CARE.has(care)) return bad('Please choose a care type');
  const shift = clean(body.shift, 40) || '12-hour day shift';
  const days = Math.min(365, Math.max(1, parseInt(body.days, 10) || 1));

  const ref = reference('NZ');
  const record = {
    reference: ref,
    care_type: care,
    shift,
    days,
    city: clean(body.city, 80),
    area: clean(body.area, 80),
    phone,
    patient: clean(body.patient, 80),
    notes: clean(body.notes, 500),
    professional: clean(body.professional, 80),
    estimate_low: Number.isFinite(body.estimate_low) ? Math.round(body.estimate_low) : null,
    estimate_high: Number.isFinite(body.estimate_high) ? Math.round(body.estimate_high) : null,
  };

  const wa = whatsappLink(env.WHATSAPP_NUMBER || '', [
    `New NURZING care request ${ref}`,
    `Care: ${care}`,
    `Shift: ${shift} · ${days} day(s)`,
    record.city || record.area ? `Where: ${[record.area, record.city].filter(Boolean).join(', ')}` : '',
    `Phone: ${phone}`,
    record.patient ? `Patient: ${record.patient}` : '',
    record.notes ? `Notes: ${record.notes}` : '',
  ]);

  // If D1 is not bound yet the request still succeeds for the customer: we hand
  // them the WhatsApp button so nothing is lost.
  if (!env.DB) {
    return json({ ok: true, reference: ref, stored: false, whatsapp: wa,
      note: 'Storage is not configured yet — please send the request on WhatsApp.' });
  }

  try {
    await env.DB.prepare(
      `INSERT INTO bookings (reference, care_type, shift, days, city, area, phone, patient, notes,
                             professional, estimate_low, estimate_high)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(record.reference, record.care_type, record.shift, record.days, record.city, record.area,
           record.phone, record.patient, record.notes, record.professional,
           record.estimate_low, record.estimate_high).run();
  } catch (err) {
    return json({ ok: true, reference: ref, stored: false, whatsapp: wa,
      note: 'We could not save it just now — please send it on WhatsApp so we do not miss you.' });
  }

  return json({ ok: true, reference: ref, stored: true, whatsapp: wa });
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const key = url.searchParams.get('key') || '';
  if (!env.ADMIN_KEY || key !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);

  const limit = Math.min(200, Math.max(1, parseInt(url.searchParams.get('limit') || '100', 10)));
  const status = url.searchParams.get('status');
  const stmt = status
    ? env.DB.prepare('SELECT * FROM bookings WHERE status = ? ORDER BY id DESC LIMIT ?').bind(status, limit)
    : env.DB.prepare('SELECT * FROM bookings ORDER BY id DESC LIMIT ?').bind(limit);
  const { results } = await stmt.all();
  return json({ ok: true, count: results.length, bookings: results });
}

export async function onRequestPut({ request, env }) {
  // update a booking's status: PUT /api/bookings?key=... {id, status}
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || (url.searchParams.get('key') || '') !== env.ADMIN_KEY) return bad('Not authorised', 401);
  if (!env.DB) return bad('Storage is not configured', 503);
  let body;
  try { body = await request.json(); } catch { return bad('Invalid JSON body'); }
  const id = parseInt(body.id, 10);
  const status = clean(body.status, 20);
  const allowed = ['new', 'contacted', 'confirmed', 'completed', 'cancelled'];
  if (!id || !allowed.includes(status)) return bad('id and a valid status are required');
  await env.DB.prepare('UPDATE bookings SET status = ? WHERE id = ?').bind(status, id).run();
  return json({ ok: true, id, status });
}
