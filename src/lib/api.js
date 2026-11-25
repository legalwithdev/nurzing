// NURZING API client.
// The app works fully offline with local demo data. Point it at the Python
// backend by setting window.NZ_API_BASE before app.js loads:
//   <script>window.NZ_API_BASE = 'https://your-api.example.com'</script>
export const API_BASE = (typeof window !== 'undefined' && window.NZ_API_BASE) || '';
export const apiEnabled = () => !!API_BASE;

let token = null;
export function setToken(t) {
  token = t || null;
  try { if (t) localStorage.setItem('nz-token', t); else localStorage.removeItem('nz-token'); } catch {}
}
export function getToken() {
  if (token) return token;
  try { token = localStorage.getItem('nz-token'); } catch {}
  return token;
}

async function req(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) { const t = getToken(); if (t) headers.Authorization = `Bearer ${t}`; }
  const res = await fetch(API_BASE + path, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new Error((data && data.detail) || `HTTP ${res.status}`);
  return data;
}

// a small cache so /nurse/:id and /book/:id can find an API-sourced record
const cache = new Map();
export function getCachedNurse(id) { return cache.get(String(id)) || null; }

export function toLocalShape(p) {
  const mapped = {
    id: 'api-' + p.id,
    apiId: p.id,
    slug: p.slug,
    name: p.name,
    role: p.designation,            // verbatim designation
    qual: p.qualification || '',
    regType: p.reg_type,
    regVerified: p.reg_verified,
    tier: p.tier,
    gold: p.gold,
    city: p.city,
    area: p.area,
    rate: Math.round((p.rate_paise || 0) / 100),
    rating: p.rating,
    reviews: p.reviews_count,
    years: p.years,
    availableToday: p.available_today,
    distanceKm: p.distance_km,
    careTypes: p.care_types || [],
    languages: p.languages || [],
    about: p.about || '',
    skills: p.care_types || [],
    verified: { id: false, police: false, insured: false, vaccinated: false },
  };
  cache.set(mapped.id, mapped);
  return mapped;
}

export const api = {
  health: () => req('/api/health'),
  meta: () => req('/api/meta'),
  professionals: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString();
    return req('/api/professionals' + (qs ? '?' + qs : ''));
  },
  professional: (id) => req(`/api/professionals/${id}`),
  quote: (payload) => req('/api/bookings/quote', { method: 'POST', body: payload }),
  createBooking: (payload) => req('/api/bookings', { method: 'POST', body: payload }),
  myBookings: () => req('/api/bookings', { auth: true }),
  requestOtp: (phone) => req('/api/auth/request-otp', { method: 'POST', body: { phone } }),
  verifyOtp: (phone, code) => req('/api/auth/verify-otp', { method: 'POST', body: { phone, code } }),
  me: () => req('/api/auth/me', { auth: true }),
  apply: (payload) => req('/api/applications', { method: 'POST', body: payload }),
  reviews: (id) => req(`/api/professionals/${id}/reviews`),
  addReview: (id, payload) => req(`/api/professionals/${id}/reviews`, { method: 'POST', body: payload, auth: true }),
};
