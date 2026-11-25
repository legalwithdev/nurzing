import { json, bad } from '../_lib.js';

export async function onRequestGet({ params, env }) {
  if (!env.DB) return bad('Storage is not configured', 503);

  const id = parseInt(params.id, 10);
  if (!id) return bad('Not found', 404);

  const { results } = await env.DB.prepare(
    `SELECT id, name, designation, qualification, years, city, area, care_types, notes,
            photo_url, verified_at, gender, status,
            docs_ok, council_ok, education_ok, pcc_ok, physical_ok, languages, shifts
       FROM applications
      WHERE id = ? AND status IN ('verified', 'profile')
      LIMIT 1`
  ).bind(id).all();

  const row = results && results[0];
  if (!row) return bad('Not found', 404);

  let care = [];
  try {
    const v = JSON.parse(row.care_types || '[]');
    if (Array.isArray(v)) care = v;
  } catch {}

  const parts = String(row.name || '').trim().split(/\\s+/);
  const display = parts.length > 1
    ? parts[0] + ' ' + parts[parts.length - 1].charAt(0) + '.'
    : parts[0] || '';

  return json({
    ok: true,
    professional: {
      id: row.id,
      name: display,
      designation: row.designation,
      qualification: row.qualification || '',
      years: row.years || 0,
      city: row.city || '',
      area: row.area || '',
      care_types: care,
      notes: row.notes || '',
      photo_url: row.photo_url || null,
      gender: row.gender || '',
      verified: row.status === 'verified',
      profile_only: row.status !== 'verified',
      verified_at: row.verified_at || null,
      checks: row.status === 'verified' ? {
        documents: !!row.docs_ok,
        council: !!row.council_ok,
        qualification: !!row.education_ok,
        pcc: !!row.pcc_ok,
        physical: !!row.physical_ok,
      } : null,
    },
  });
}
