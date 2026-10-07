import { Link } from 'react-router-dom';
import { NURSES } from '../data/nurses.js';
import { useBookings } from '../lib/store.jsx';
import NurseCard from '../components/NurseCard.jsx';
import { HeartIcon, CompassIcon } from '../lib/icons.jsx';

export default function Saved() {
  const { saved } = useBookings();
  const list = NURSES.filter((n) => saved.includes(n.id));

  return (
    <div className="fade">
      <span className="eyebrow">Shortlist</span>
      <h1 style={{ margin: '8px 0 14px' }}>Saved professionals</h1>
      {list.length ? (
        <div className="grid">{list.map((n) => <NurseCard key={n.id} nurse={n} />)}</div>
      ) : (
        <div className="empty">
          <div className="eic"><HeartIcon size={26} /></div>
          <h3>Nothing saved yet</h3>
          <p>Tap the heart on any professional to shortlist them.</p>
          <Link to="/" className="btn btn-gold" style={{ marginTop: 14 }}><CompassIcon size={16} /> Discover nurses</Link>
        </div>
      )}
    </div>
  );
}
