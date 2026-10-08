import { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { BookingsProvider, useBookings } from '../lib/store.jsx';
import { CompassIcon, CalendarIcon, HeartIcon, UserIcon, PinIcon, CheckIcon } from '../lib/icons.jsx';

const SEO = [
  ['/nurse/', 'Nurse profile \u2014 NURZING', 'Verified professional: experience, skills and reviews.'],
  ['/book/', 'Book a nurse \u2014 NURZING', 'Book home nursing care with a transparent, upfront estimate.'],
  ['/bookings', 'My bookings \u2014 NURZING', 'Track your home care bookings and their live status.'],
  ['/saved', 'Saved professionals \u2014 NURZING', 'Your shortlist of nurses and attendants.'],
  ['/account', 'Account \u2014 NURZING', 'Your NURZING profile and care preferences.'],
];

function useSeo(pathname) {
  useEffect(() => {
    let title = 'NURZING \u2014 Book verified nurses at home';
    let desc = 'Discover nurses and attendants, see transparent pricing, and book home care in minutes.';
    for (const [prefix, t, d] of SEO) {
      if (pathname.startsWith(prefix)) { title = t; desc = d; break; }
    }
    document.title = title;
    let m = document.querySelector('meta[name="description"]');
    if (!m) { m = document.createElement('meta'); m.setAttribute('name', 'description'); document.head.appendChild(m); }
    m.setAttribute('content', desc);
  }, [pathname]);
}

function Shell() {
  const { toastMsg } = useBookings();
  const { pathname } = useLocation();
  useSeo(pathname);
  return (
    <div className="app">
      <div className="demo-strip">DEMO — sample professionals &amp; reviews. Replace with your real data before launch.</div>
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand">
            <svg className="mark" viewBox="0 0 40 40" fill="none">
              <circle cx="20" cy="20" r="18.2" stroke="#C69C42" strokeWidth="1.4" />
              <path d="M14 27V13l12 14V13" stroke="#073331" strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            NURZING
          </NavLink>
          <span className="loc-chip"><PinIcon size={14} /> Bengaluru</span>
          <NavLink to="/saved" className="icon-btn" style={{ position: 'relative' }} aria-label="Saved nurses">
            <HeartIcon size={18} />
          </NavLink>
        </div>
      </header>

      <main className="screen"><Outlet /></main>

      <nav className="dock" aria-label="App navigation">
        <div className="dock-inner">
          <NavLink to="/" end><CompassIcon />Discover</NavLink>
          <NavLink to="/bookings"><CalendarIcon />Bookings</NavLink>
          <NavLink to="/saved"><HeartIcon />Saved</NavLink>
          <NavLink to="/account"><UserIcon />Account</NavLink>
        </div>
      </nav>

      {toastMsg && <div className="toast"><CheckIcon size={16} /> {toastMsg}</div>}
    </div>
  );
}

export default function AppShell() {
  return (
    <BookingsProvider>
      <Shell />
    </BookingsProvider>
  );
}
