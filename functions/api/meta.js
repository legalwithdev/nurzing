import { json } from './_lib.js';

export const CARE_TYPES = [
  'Home Nursing',
  'Live-in Nursing (24x7)',
  'Elderly Care & Attendants',
  'Post-Surgical Recovery',
  'Mother & Baby Care',
  'Physiotherapy at Home',
  'ICU-Trained Nurses',
];

export const SHIFTS = [
  '12-hour day shift',
  '12-hour night shift',
  '24-hour live-in',
  'Hourly visit',
];

export const CITIES = ['Bengaluru', 'Mumbai', 'Delhi NCR', 'Hyderabad', 'Pune', 'Chennai'];

export async function onRequestGet() {
  return json({ ok: true, care_types: CARE_TYPES, shifts: SHIFTS, cities: CITIES });
}
