import { Link } from 'react-router-dom';
import { useBookings, STAGES } from '../lib/store.jsx';
import { inr } from '../lib/pricing.js';
import { CalendarIcon, PinIcon, ClockIcon, CompassIcon } from '../lib/icons.jsx';

const fmt = (t) => new Date(t).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });

export default function Bookings() {
  const { bookings, advanceBooking, cancelBooking } = useBookings();

  if (!bookings.length) {
    return (
      <div className="fade">
        <span className="eyebrow">Your care</span>
        <h1 style={{ margin: '8px 0 14px' }}>My bookings</h1>
        <div className="empty">
          <div className="eic"><CalendarIcon size={26} /></div>
          <h3>No bookings yet</h3>
          <p>Find a verified nurse and book in under a minute.</p>
          <Link to="/" className="btn btn-gold" style={{ marginTop: 14 }}><CompassIcon size={16} /> Discover nurses</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="fade">
      <span className="eyebrow">Your care</span>
      <h1 style={{ margin: '8px 0 14px' }}>My bookings</h1>

      {bookings.map((b) => {
        const done = b.statusIndex >= STAGES.length - 1;
        return (
          <div className="booking-card" key={b.id}>
            <div className="bc-head">
              <div>
                <div className="nc-name">{b.nurseName}</div>
                <div className="nc-sub">{b.careType} &middot; {b.shiftLabel} &middot; {b.days} {b.unit === 'visit' ? 'visit(s)' : 'day(s)'}</div>
              </div>
              <span className={'status-tag' + (done ? '' : ' live')}>{STAGES[b.statusIndex]}</span>
            </div>

            <div className="nc-sub" style={{ marginTop: 10, display: 'flex', gap: 14, flexWrap: 'wrap' }}>
              <span style={{ display: 'flex', gap: 5, alignItems: 'center' }}><CalendarIcon size={14} /> {b.date}</span>
              <span style={{ display: 'flex', gap: 5, alignItems: 'center' }}><PinIcon size={14} /> {b.address || '\u2014'}</span>
              <span style={{ display: 'flex', gap: 5, alignItems: 'center' }}><ClockIcon size={14} /> {inr(b.total)}</span>
            </div>

            <div className="tl">
              {STAGES.map((s, i) => (
                <div key={s} className={'tl-item ' + (i < b.statusIndex ? 'done' : i === b.statusIndex ? 'now' : 'todo')}>
                  <span className="tl-dot" />
                  <div className="tl-title">{s}</div>
                  {b.stageTimes[i] && <div className="tl-time">{fmt(b.stageTimes[i])}</div>}
                </div>
              ))}
            </div>

            <div className="nav-row" style={{ marginTop: 12 }}>
              {!done
                ? <button className="btn btn-dark" onClick={() => advanceBooking(b.id)}>Advance status (demo)</button>
                : <span className="muted" style={{ fontSize: '.82rem' }}>Care completed</span>}
              <button className="btn btn-ghost" onClick={() => cancelBooking(b.id)}>Cancel</button>
            </div>
            <div className="muted" style={{ fontSize: '.74rem', marginTop: 8 }}>Booking ID {b.id}</div>
          </div>
        );
      })}
    </div>
  );
}
