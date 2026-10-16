const KEY = 'nz-theme';

export function applyTheme(t) {
  const d = t === 'dark' || (t !== 'light' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.setAttribute('data-theme', d ? 'dark' : 'light');
  const m = document.querySelector('meta[name=theme-color]');
  if (m) m.setAttribute('content', d ? '#081918' : '#062A28');
}

export function getTheme() {
  try { return localStorage.getItem(KEY) || 'auto'; } catch { return 'auto'; }
}

export function setTheme(t) {
  try { localStorage.setItem(KEY, t); } catch {}
  applyTheme(t);
}
