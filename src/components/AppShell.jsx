import { Outlet, NavLink } from 'react-router-dom';
import { BookingsProvider, useBookings } from '../lib/store.jsx';
import { CompassIcon, CalendarIcon, HeartIcon, UserIcon, PinIcon, CheckIcon } from '../lib/icons.jsx';

function Shell() {
  const { toastMsg } = useBookings();
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
