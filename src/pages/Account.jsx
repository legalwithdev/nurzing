import { useBookings } from '../lib/store.jsx';
import { UserIcon, ShieldIcon, PhoneIcon, ChevronIcon } from '../lib/icons.jsx';

const rows = [
  { icon: ShieldIcon, label: 'Care preferences', sub: 'Languages, shift, budget' },
  { icon: PhoneIcon, label: 'Contact & support', sub: '24x7 care advisor' },
  { icon: ShieldIcon, label: 'Verification & safety', sub: 'How we vet professionals' },
];

export default function Account() {
  const { bookings, saved } = useBookings();
  const active = bookings.filter((b) => b.statusIndex < 4).length;

  return (
    <div className="fade">
      <span className="eyebrow">Your account</span>
      <h1 style={{ margin: '8px 0 14px' }}>Profile</h1>

      <div className="card" style={{ padding: 20 }}>
        <div className="profile-head">
          <span className="avatar"><span>D</span></span>
          <div style={{ flex: 1 }}>
            <div className="nc-name">dev</div>
            <div className="nc-sub">Bengaluru &middot; 918013968142@phone.sarvam.ai</div>
          </div>
        </div>
        <div className="stat-row">
          <div className="stat-box"><div className="n">{bookings.length}</div><div className="l">Bookings</div></div>
          <div className="stat-box"><div className="n">{active}</div><div className="l">Active now</div></div>
          <div className="stat-box"><div className="n">{saved.length}</div><div className="l">Saved</div></div>
        </div>
      </div>

      <div className="section-title"><h2>Settings</h2></div>
      <div className="card" style={{ padding: '4px 18px' }}>
        {rows.map((r, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '16px 0', borderTop: i ? '1px solid var(--line-2)' : 'none' }}>
            <span style={{ width: 38, height: 38, borderRadius: 12, background: 'rgba(10,64,60,.06)', display: 'grid', placeItems: 'center', color: 'var(--teal-700)' }}>
              <r.icon size={18} />
            </span>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: '.94rem' }}>{r.label}</div>
              <div className="muted" style={{ fontSize: '.8rem' }}>{r.sub}</div>
            </div>
            <ChevronIcon size={16} />
          </div>
        ))}
      </div>

      <p className="muted" style={{ fontSize: '.76rem', marginTop: 20, lineHeight: 1.6 }}>
        DEMO BUILD: every professional, rating, review and verification badge in this app is sample data and must be replaced with verified, real information before launch. NURZING is a nursing bureau and placement service. Rates shown are indicative and confirmed by your care advisor before care begins. This build stores data only in your browser.
      </p>
    </div>
  );
}
