import { useMemo, useState } from 'react';
import { NURSES, CITIES } from '../data/nurses.js';
import { CARE_TYPES } from '../lib/pricing.js';
import NurseCard from '../components/NurseCard.jsx';
import { SearchIcon } from '../lib/icons.jsx';

export default function Discover() {
  const [q, setQ] = useState('');
  const [care, setCare] = useState('All');
  const [city, setCity] = useState('All');
  const [sort, setSort] = useState('rating');

  const list = useMemo(() => {
    let r = NURSES.filter((n) => {
      if (care !== 'All' && !n.careTypes.includes(care)) return false;
      if (city !== 'All' && n.city !== city) return false;
      if (q) {
        const hay = (n.name + ' ' + n.area + ' ' + n.city + ' ' + n.skills.join(' ') + ' ' + n.careTypes.join(' ')).toLowerCase();
        if (!hay.includes(q.toLowerCase())) return false;
      }
      return true;
    });
    if (sort === 'rating') r = [...r].sort((a, b) => b.rating - a.rating);
    if (sort === 'price') r = [...r].sort((a, b) => a.rate - b.rate);
    if (sort === 'distance') r = [...r].sort((a, b) => a.distanceKm - b.distanceKm);
    return r;
  }, [q, care, city, sort]);

  return (
    <div className="fade">
      <span className="eyebrow">Verified home care</span>
      <h1 style={{ margin: '8px 0 6px' }}>Find care that fits your family</h1>
      <p className="muted" style={{ maxWidth: '40rem' }}>
        Browse background-verified nurses and attendants, see transparent daily rates, and book in minutes.
      </p>

      <div className="searchbar" style={{ marginTop: 18 }}>
        <SearchIcon />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, skill or area" aria-label="Search nurses" />
      </div>

      <div className="filters">
        <button className={'chip' + (care === 'All' ? ' sel' : '')} onClick={() => setCare('All')}>All care</button>
        {CARE_TYPES.map((c) => (
          <button key={c} className={'chip' + (care === c ? ' sel' : '')} onClick={() => setCare(c)}>{c}</button>
        ))}
      </div>

      <div className="filter-bar">
        <select className="ctl" style={{ width: 'auto' }} value={city} onChange={(e) => setCity(e.target.value)} aria-label="City">
          <option value="All">All cities</option>
          {CITIES.map((c) => <option key={c}>{c}</option>)}
        </select>
        <select className="ctl" style={{ width: 'auto' }} value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort">
          <option value="rating">Top rated</option>
          <option value="price">Lowest price</option>
          <option value="distance">Nearest</option>
        </select>
        <span className="muted" style={{ fontSize: '.82rem', marginLeft: 'auto' }}>{list.length} professionals</span>
      </div>

      {list.length ? (
        <div className="grid" style={{ marginTop: 16 }}>
          {list.map((n) => <NurseCard key={n.id} nurse={n} />)}
        </div>
      ) : (
        <div className="empty">
          <div className="eic"><SearchIcon size={26} /></div>
          <h3>No matches</h3>
          <p>Try a different care type or city.</p>
        </div>
      )}
    </div>
  );
}
