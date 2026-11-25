import { json, bad, clean, throttled, ipOf } from '../_lib.js';

// Placeholder rates - replace with your real rates before going live.
const RATES = {
  'Home Nursing': { day: 1400, night: 1600, live: 2800 },
  'Live-in Nursing (24x7)': { day: 2800, night: 2800, live: 2800 },
  'Elderly Care & Attendants': { day: 1100, night: 1250, live: 2200 },
  'Post-Surgical Recovery': { day: 1600, night: 1800, live: 3000 },
  'Mother & Baby Care': { day: 1700, night: 1900, live: 3200 },
  'Physiotherapy at Home': { day: 900, night: 900, live: 900 },
  'ICU-Trained Nurses': { day: 2200, night: 2400, live: 3800 },
};

const CARE = new Set(Object.keys(RATES));

export async function onRequestPost({ request }) {
  if (throttled('q:' + ipOf(request), 40)) return bad('Too many requests', 429);

  let body;
  try {
    body = await request.json();
  } catch {
    return bad('Invalid JSON body');
  }

  const care = clean(body.care_type, 60);
  if (!CARE.has(care)) return bad('Please choose a care type');

  const shift = clean(body.shift, 40) || '12-hour day shift';
  const days = Math.min(365, Math.max(1, parseInt(body.days, 10) || 1));

  const row = RATES[care];
  // Order matters: "12-hour day shift" must not be treated as an hourly visit.
  let perDay;
  if (/^hourly|per hour/i.test(shift)) perDay = Math.round(row.day / 6);
  else if (/24|live/i.test(shift)) perDay = row.live;
  else if (/night/i.test(shift)) perDay = row.night;
  else perDay = row.day;

  const low = perDay * days;
  const high = Math.round(low * 1.25);

  return json({
    ok: true,
    care_type: care,
    shift,
    days,
    per_day: perDay,
    low,
    high,
    currency: 'INR',
    indicative: true,
    note: 'Indicative range only. A NURZING advisor confirms the final price before anything is booked.',
  });
}
