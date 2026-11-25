import { Link } from 'react-router-dom';
import { useBookings } from '../lib/store.jsx';
import { isGold } from '../data/nurses.js';
import Stars from './Stars.jsx';
import { HeartIcon, PinIcon, CheckIcon } from '../lib/icons.jsx';
import { inr } from '../lib/pricing.js';

// Privacy: the card shows a first name and a last initial only.
function shortName(v) {
  const parts = String(v || '').trim().split(/\s+/);
  if (parts.length > 1) return parts[0] + ' ' + parts[parts.length - 1].charAt(0) + '.';
  return parts[0] || '';
}

const CHECKS = [
  ['documents', 'Government ID & documents'],
  ['council', 'Nursing council registration'],
  ['qualification', 'Qualification certificates'],
  ['pcc', 'Police clearance (PCC)'],
  ['physical', 'In-person physical verification'],
];

export default function NurseCard({ nurse }) {
  const { isSaved, toggleSaved } = useBookings();
  const on = isSaved(nurse.id);
  const name = shortName(nurse.name);
  const initials = name.split(' ').map((w) => w[0]).slice(0, 2).join('');
  const place = [nurse.area, nurse.city].filter(Boolean).join(', ');

  return (
    <article className="nurse-card fade">
      <button
        className={'save-btn' + (on ? ' on' : '')}
        aria-label={on ? 'Remove from saved' : 'Save professional'}
        onClick={() => toggleSaved(nurse.id)}
      >
        <HeartIcon />
      </button>

      <Link to={`/nurse/${nurse.id}`} className="nc-top">
        <span className="avatar">
          {nurse.photo
            ? <img src={nurse.photo} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
            : <span>{initials}</span>}
        </span>
        <div>
          <div className="nc-name">{name}</div>
          <div className="nc-sub">{nurse.role}{nurse.years ? ' \u00b7 ' + nurse.years + ' yrs' : ''}</div>
          {nurse.reviews > 0 && <Stars rating={nurse.rating} count={nurse.reviews} />}
        </div>
      </Link>

      <div className="nc-badges">
        {!nurse.apiId && (
          <span className="pill" style={{ background: '#EFE7D6', color: '#7A6A45', fontWeight: 700 }}>
            Sample profile
          </span>
        )}
        {isGold(nurse) && (
          <span className="gold-badge" title="B.Sc Nursing + RN&RM + experience + specialisation">&#9733; NURZING GOLD</span>
        )}
        {nurse.profileOnly && (
          <span className="pill" style={{ background: '#F7E9D2', color: '#8A4B12', fontWeight: 700 }}>
            Profile only &middot; not verified for work
          </span>
        )}
        {nurse.gender && <span className="pill pill-teal">{nurse.gender}</span>}
        {nurse.careTypes.slice(0, 3).map((c) => <span key={c} className="pill pill-teal">{c}</span>)}
        {(nurse.languages || []).map((l) => <span key={'l-' + l} className="pill pill-teal">{l}</span>)}
        {(nurse.shifts || []).map((sh) => <span key={'s-' + sh} className="pill pill-teal">{sh}</span>)}
        {!nurse.profileOnly && nurse.availableToday && <span className="pill pill-gold">Today</span>}
      </div>

      {place && (
        <div className="nc-sub" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <PinIcon size={14} /> {place}{nurse.distanceKm ? ' \u00b7 ' + nurse.distanceKm + ' km' : ''}
        </div>
      )}

      {(nurse.qual && nurse.qual !== 'Other') || (nurse.regType && nurse.regType !== 'none') ? (
        <div className="nc-reg">
          {nurse.qual && nurse.qual !== 'Other' && <span className="q">{nurse.qual}</span>}
          {nurse.regVerified
            ? <span className="ok"><CheckIcon size={13} /> {nurse.regType} verified</span>
            : (nurse.regType && nurse.regType !== 'none')
              ? <span className="warn">Registration not verified</span>
              : null}
        </div>
      ) : null}

      {!nurse.profileOnly && nurse.checks && (
        <div className="nc-verified" style={{ marginTop: 8, padding: '10px 12px', background: 'rgba(29,122,79,.08)', border: '1px solid rgba(29,122,79,.25)', borderRadius: 10 }}>
          <div style={{ fontSize: '.72rem', letterSpacing: '.08em', textTransform: 'uppercase', fontWeight: 700, color: '#1D7A4F', marginBottom: 6 }}>
            Verified by NURZING
          </div>
          {CHECKS.map(([k, label]) => (
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
        {nurse.profileOnly
          ? <div className="nc-sub" style={{ fontSize: '.82rem' }}>Not bookable until verified</div>
          : <div className="price">{nurse.rate ? inr(nurse.rate) : 'Price on request'}{nurse.rate ? <small> /day</small> : null}</div>}
        {nurse.profileOnly
          ? <Link to={`/nurse/${nurse.id}`} className="btn btn-ghost">View profile</Link>
          : <Link to={`/book/${nurse.id}`} className="btn btn-gold">Book <span aria-hidden="true">&rarr;</span></Link>}
      </div>
    </article>
  );
}
