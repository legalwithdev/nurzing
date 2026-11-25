// GET /api/professionals -> ONLY verified professionals, in the shape the
// customer app's nurse cards expect.
//
// Tier rules (standing rule, must never drift):
//   1 = B.Sc Nursing + RN&RM + 7+ years + a specialisation   -> GOLD
//   2 = RN&RM / RANM
//   3 = other licensed profession (physio, etc.)
//   4 = non-medical support (attendant, ward boy, GDA)
import { json, bad } from '../_lib.js';

const SUPPORT = ['attendant', 'ward boy', 'wardboy', 'caregiver', 'nursing assistant', 'gda', 'ayah', 'helper'];
const LICENSED_OTHER = ['physiotherap', 'occupational therap', 'dietitian', 'nutritionist'];
const GOLD_MIN_YEARS = 7;

function tierFor(qualification, regType, years, designation) {
  const q = String(qualification || '').toLowerCase().trim();
  const d = String(designation || '').toLowerCase();
  const yrs = Number(years) || 0;
  const specialised = /\([^)]+\)/.test(String(designation || ''));

  if (SUPPORT.some((w) => d.includes(w))) return { tier: 4, gold: 0 };
  if (LICENSED_OTHER.some((w) => d.includes(w))) return { tier: 3, gold: 0 };
  if (regType === 'RN&RM') {
    if ((q === 'b.sc nursing' || q === 'bsc nursing' || q === 'b.sc. nursing') && yrs >= GOLD_MIN_YEARS && specialised) {
      return { tier: 1, gold: 1 };
    }
    return { tier: 2, gold: 0 };
  }
  if (regType === 'RANM') return { tier: 2, gold: 0 };
  return { tier: 4, gold: 0 };
}

function parseCares(raw) {
  try { const v = JSON.parse(raw || '[]'); return Array.isArray(v) ? v : []; } catch { return []; }
}

export async function onRequestGet({ env }) {
  if (!env.DB) return bad('Storage is not configured', 503);

  const { results } = await env.DB.prepare(
    `SELECT id, name, designation, qualification, reg_type, reg_number, years, city, area,
            care_types, notes, verified_at, photo_url, gender, status,
            docs_ok, council_ok, education_ok, pcc_ok, physical_ok
       FROM applications
      WHERE status IN ('verified', 'profile')
      ORDER BY (status = 'verified') DESC, years DESC, id DESC
      LIMIT 200`
  ).all();

  const items = (results || []).map((r) => {
    const t = tierFor(r.qualification, r.reg_type, r.years, r.designation);
    return {
      id: r.id,
      slug: 'nz-' + r.id,
      name: r.name,
      designation: r.designation,
      qualification: r.qualification || '',
      reg_type: r.reg_type,
      reg_verified: r.status === 'verified',
      profile_only: r.status === 'profile',
      gender: r.gender || '',
      photo_url: r.photo_url || null,
      checks: r.status === 'verified' ? {
        documents: !!r.docs_ok,
        council: !!r.council_ok,
        qualification: !!r.education_ok,
        pcc: !!r.pcc_ok,
        physical: !!r.physical_ok,
      } : null,
      reg_number: r.reg_number || null,
      years: r.years || 0,
      city: r.city || '',
      area: r.area || '',
      care_types: parseCares(r.care_types),
      about: r.notes || '',
      verified_at: r.verified_at,
      tier: t.tier,
      gold: !!t.gold,
    };
  });

  // tier is always the primary sort
  items.sort((a, b) => a.tier - b.tier || b.years - a.years);

  return json({ ok: true, total: items.length, items });
}
