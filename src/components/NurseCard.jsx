import { Link } from 'react-router-dom';
import { useBookings } from '../lib/store.jsx';
import Stars from './Stars.jsx';
import { HeartIcon, PinIcon } from '../lib/icons.jsx';
import { inr } from '../lib/pricing.js';

export default function NurseCard({ nurse }) {
  const { isSaved, toggleSaved } = useBookings();
  const on = isSaved(nurse.id);
  const initials = nurse.name.split(' ').map((w) => w[0]).slice(0, 2).join('');
  return (
    <article className="nurse-card fade">
      <button
        className={'save-btn' + (on ? ' on' : '')}
        aria-label={on ? 'Remove from saved' : 'Save nurse'}
        onClick={() => toggleSaved(nurse.id)}
      >
        <HeartIcon />
      </button>
      <Link to={`/nurse/${nurse.id}`} className="nc-top">
        <span className="avatar"><span>{initials}</span></span>
        <div>
          <div className="nc-name">{nurse.name}</div>
          <div className="nc-sub">{nurse.role} &middot; {nurse.years} yrs</div>
          <Stars rating={nurse.rating} count={nurse.reviews} />
        </div>
      </Link>
      <div className="nc-badges">
        {nurse.careTypes.slice(0, 3).map((c) => (
          <span key={c} className="pill pill-teal">{c}</span>
        ))}
        {nurse.availableToday && <span className="pill pill-gold">Today</span>}
      </div>
      <div className="nc-sub" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <PinIcon size={14} /> {nurse.area}, {nurse.city} &middot; {nurse.distanceKm} km
      </div>
      <div className="nc-foot">
        <div className="price">{inr(nurse.rate)}<small> /day</small></div>
        <Link to={`/book/${nurse.id}`} className="btn btn-gold">Book <span aria-hidden="true">&rarr;</span></Link>
      </div>
    </article>
  );
}
