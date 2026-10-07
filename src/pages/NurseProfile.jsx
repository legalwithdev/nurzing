import { Link, useParams } from 'react-router-dom';
import { getNurse } from '../data/nurses.js';
import Stars from '../components/Stars.jsx';
import { BackIcon, PinIcon, CheckIcon } from '../lib/icons.jsx';
import { inr } from '../lib/pricing.js';

export default function NurseProfile() {
  const { id } = useParams();
  const n = getNurse(id);
  if (!n) {
    return (
      <div className="empty">
        <h3>Professional not found</h3>
        <Link className="btn btn-gold" to="/" style={{ marginTop: 12 }}>Back to discover</Link>
      </div>
    );
  }
  const initials = n.name.split(' ').map((w) => w[0]).slice(0, 2).join('');
  return (
    <div className="fade">
      <Link to="/" className="back-link"><BackIcon size={16} /> Back</Link>

      <div className="card" style={{ padding: 20 }}>
        <div className="profile-head">
          <span className="avatar"><span>{initials}</span></span>
          <div style={{ flex: 1, minWidth: 190 }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
              <h1 style={{ fontSize: '1.5rem' }}>{n.name}</h1>
              <span className="pill pill-gold">Verified</span>
            </div>
            <div className="muted" style={{ marginTop: 2 }}>{n.role} &middot; {n.city}</div>
            <div style={{ marginTop: 6 }}><Stars rating={n.rating} count={n.reviews} /></div>
            <div className="nc-sub" style={{ marginTop: 6, display: 'flex', gap: 6, alignItems: 'center' }}>
              <PinIcon size={14} /> {n.area} &middot; {n.distanceKm} km away
            </div>
          </div>
        </div>

        <div className="stat-row">
          <div className="stat-box"><div className="n">{n.years} yrs</div><div className="l">Experience</div></div>
          <div className="stat-box"><div className="n">{n.reviews}</div><div className="l">Reviews</div></div>
          <div className="stat-box"><div className="n">{n.rating}</div><div className="l">Rating</div></div>
        </div>

        <div className="chip-row" style={{ marginTop: 16 }}>
          {n.verified.id && <span className="chip"><CheckIcon size={13} /> ID verified</span>}
          {n.verified.police && <span className="chip"><CheckIcon size={13} /> Police verified</span>}
          {n.verified.insured && <span className="chip"><CheckIcon size={13} /> Insured</span>}
          {n.verified.vaccinated && <span className="chip"><CheckIcon size={13} /> Vaccinated</span>}
        </div>
        <p className="muted" style={{ fontSize: '.74rem', marginTop: 10 }}>Demo verification badges — replace with your real, verifiable checks.</p>
      </div>

      <div className="section-title"><h2>About</h2></div>
      <div className="card" style={{ padding: 20 }}>
        <p style={{ color: '#33413f' }}>{n.about}</p>
        <h3 style={{ margin: '16px 0 8px', fontSize: '.95rem' }}>Skills</h3>
        <div className="skills">{n.skills.map((s) => <span key={s} className="pill pill-teal">{s}</span>)}</div>
        <h3 style={{ margin: '16px 0 8px', fontSize: '.95rem' }}>Care types</h3>
        <div className="skills">{n.careTypes.map((s) => <span key={s} className="chip">{s}</span>)}</div>
        <h3 style={{ margin: '16px 0 8px', fontSize: '.95rem' }}>Languages</h3>
        <div className="skills">{n.languages.map((s) => <span key={s} className="chip">{s}</span>)}</div>
      </div>

      <div className="section-title"><h2>Reviews</h2><span className="link">{n.reviews} total</span></div>
      <p className="muted" style={{ fontSize: '.74rem', margin: '-6px 0 10px' }}>Sample reviews for demo — replace with real, consented reviews.</p>
      <div className="card" style={{ padding: '4px 20px' }}>
        {n.reviewsList.map((r, i) => (
          <div className="review" key={i}>
            <span className="rav">{r.name[0]}</span>
            <div>
              <div className="rname">{r.name} <span className="muted" style={{ fontWeight: 400, fontSize: '.78rem' }}>&middot; {r.role} &middot; {r.when}</span></div>
              <Stars rating={r.stars} />
              <div className="rtext">{r.text}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="sticky-cta">
        <div className="card" style={{ padding: 14, display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div className="price">{inr(n.rate)}<small> /day</small></div>
            <div className="muted" style={{ fontSize: '.76rem' }}>Transparent &middot; no hidden charges</div>
          </div>
          <Link to={`/book/${n.id}`} className="btn btn-gold btn-lg">Book now</Link>
        </div>
      </div>
    </div>
  );
}
