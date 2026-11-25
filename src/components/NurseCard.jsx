import { Link } from 'react-router-dom';
import { useBookings } from '../lib/store.jsx';
import { isGold } from '../data/nurses.js';
import Stars from './Stars.jsx';
import { HeartIcon, PinIcon, CheckIcon } from '../lib/icons.jsx';
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
        {isGold(nurse) && (
          <span className="gold-badge" title="B.Sc Nursing + RN&RM + experience + specialisation">&#9733; NURZING GOLD</span>
        )}
        {nurse.careTypes.slice(0, 3).map((c) => (
          <span key={c} className="pill pill-teal">{c}</span>
        ))}
        {nurse.availableToday && <span className="pill pill-gold">Today</span>}
      </div>
      <div className="nc-sub" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <PinIcon size={14} /> {nurse.area}, {nurse.city} &middot; {nurse.distanceKm} km
      </div>
      {/* Registration is separate from the designation; a badge shows only when actually verified. */}
      {(nurse.qual || nurse.regVerified || (nurse.regType && nurse.regType !== 'none')) && (
        <div className="nc-reg">
          {nurse.qual && <span className="q">{nurse.qual}</span>}
          {nurse.regVerified
            ? <span className="ok"><CheckIcon size={13} /> {nurse.regType} verified</span>
            : (nurse.regType && nurse.regType !== 'none')
              ? <span className="warn">Registration not verified</span>
              : null}
        </div>
      )}
      {!nurse.profileOnly && nurse.checks && (
        <div className="nc-verified" style={{ marginTop: 8, padding: '10px 12px', background: 'rgba(29,122,79,.08)', border: '1px solid rgba(29,122,79,.25)', borderRadius: 10 }}>
          <div style={{ fontSize: '.72rem', letterSpacing: '.08em', textTransform: 'uppercase', fontWeight: 700, color: '#1D7A4F', marginBottom: 6 }}>
            Verified by NURZING
          </div>
          {[
            ['documents', 'Government ID & documents'],
            ['council', 'Nursing council registration'],
            ['qualification', 'Qualification certificates'],
            ['pcc', 'Police clearance (PCC)'],
            ['physical', 'In-person physical verification'],
          ].map(([k, label]) => (
            <div key={k} style={{ display: 'flex', gap: 6, fontSize: '.82rem', lineHeight: 1.6, opacity: nurse.checks[k] ? 1 : 0.45 }}>
              <span style={{ color: nurse.checks[k] ? '#1D7A4F' : '#9a9689', fontWeight: 700 }}>
                {nurse.checks[k] ? '\u2713' : '\u2013'}
              </span>
              <span>{label}</span>
            </div>
          ))}
        </div>
      )}

      <div className="nc-foot">
        <div className="price">[&#8377;0,000]<small> /day</small></div>
        <Link to={`/book/${nurse.id}`} className="btn btn-gold">Book <span aria-hidden="true">&rarr;</span></Link>
      </div>
    </article>
  );
}
