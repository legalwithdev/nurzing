import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getNurse } from '../data/nurses.js';
import { SHIFTS, quote, inr } from '../lib/pricing.js';
import { useBookings } from '../lib/store.jsx';
import { BackIcon, CheckIcon } from '../lib/icons.jsx';

export default function BookingFlow() {
  const { id } = useParams();
  const n = getNurse(id);
  const nav = useNavigate();
  const { addBooking, toast } = useBookings();

  const [step, setStep] = useState(1);
  const [care, setCare] = useState(n ? n.careTypes[0] : 'Home Nursing');
  const [shift, setShift] = useState('day12');
  const [days, setDays] = useState(7);
  const [date, setDate] = useState(() => new Date(Date.now() + 86400000).toISOString().slice(0, 10));
  const [addr, setAddr] = useState('');
  const [patient, setPatient] = useState('');
  const [phone, setPhone] = useState('');
  const [notes, setNotes] = useState('');

  if (!n) {
    return <div className="empty"><h3>Professional not found</h3><Link className="btn btn-gold" to="/" style={{ marginTop: 12 }}>Back</Link></div>;
  }

  const q = quote(n, care, shift, days);
  const canNext = step === 1 ? !!care : step === 2 ? !!shift : (addr.trim().length > 4 && phone.trim().length >= 8);

  function next() {
    if (step < 3) { setStep(step + 1); return; }
    const b = addBooking({
      nurseId: n.id, nurseName: n.name, careType: care, shiftId: shift, shiftLabel: q.shift.label,
      days: q.days, date, address: addr, patient, phone, notes, total: q.total, unit: q.unit,
    });
    toast('Booking requested \u00B7 ' + b.id);
    nav('/bookings');
  }

  return (
    <div className="fade">
      <Link to={`/nurse/${n.id}`} className="back-link"><BackIcon size={16} /> Back</Link>
      <h1 style={{ marginBottom: 4 }}>Book {n.name.split(' ')[0]}</h1>
      <p className="muted" style={{ marginBottom: 18 }}>Three quick steps. See the price before you commit.</p>

      <div className="steps">
        {[1, 2, 3].map((s) => <i key={s} className={step >= s ? 'on' : ''} />)}
      </div>

      <div className="card" style={{ padding: 20 }}>
        {step === 1 && (
          <>
            <span className="eyebrow">Step 1 of 3</span>
            <h2 style={{ margin: '6px 0 14px' }}>What kind of care?</h2>
            <div className="opt-grid">
              {n.careTypes.map((c) => (
                <button key={c} className={'opt' + (care === c ? ' sel' : '')} onClick={() => setCare(c)}>{c}</button>
              ))}
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <span className="eyebrow">Step 2 of 3</span>
            <h2 style={{ margin: '6px 0 14px' }}>Shift &amp; duration</h2>
            <div className="opt-grid">
              {SHIFTS.map((s) => (
                <button key={s.id} className={'opt' + (shift === s.id ? ' sel' : '')} onClick={() => setShift(s.id)}>
                  <span><b style={{ display: 'block' }}>{s.label}</b><small className="muted">{s.sub}</small></span>
                </button>
              ))}
            </div>
            <div className="field">
              <label>Start date</label>
              <input className="ctl" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
            </div>
            {q.unit === 'day' && (
              <div className="field">
                <label>Number of days</label>
                <select className="ctl" value={days} onChange={(e) => setDays(Number(e.target.value))}>
                  <option value={1}>1 day</option>
                  <option value={3}>3 days</option>
                  <option value={7}>7 days</option>
                  <option value={15}>15 days</option>
                  <option value={30}>30 days</option>
                </select>
              </div>
            )}
          </>
        )}

        {step === 3 && (
          <>
            <span className="eyebrow">Step 3 of 3</span>
            <h2 style={{ margin: '6px 0 14px' }}>Where should we come?</h2>
            <div className="field">
              <label>Full address</label>
              <textarea className="ctl" rows={3} value={addr} onChange={(e) => setAddr(e.target.value)} placeholder="Flat, building, street, area, city" />
            </div>
            <div className="field">
              <label>Patient name</label>
              <input className="ctl" value={patient} onChange={(e) => setPatient(e.target.value)} placeholder="Who is the care for?" />
            </div>
            <div className="field">
              <label>Mobile number</label>
              <input className="ctl" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91" />
            </div>
            <div className="field">
              <label>Notes for the nurse (optional)</label>
              <textarea className="ctl" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Conditions, medication, preferences" />
            </div>
          </>
        )}
      </div>

      <div className="summary" style={{ marginTop: 16 }}>
        <div className="lab">Live estimate</div>
        <div className="big">{inr(q.total)} <small>{q.unit === 'visit' ? 'per visit' : `for ${q.days} day${q.days > 1 ? 's' : ''}`}</small></div>
        <div className="rows">
          <div className="row"><span>Professional</span><b>{n.name}</b></div>
          <div className="row"><span>Care type</span><b>{care}</b></div>
          <div className="row"><span>Shift</span><b>{q.shift.label}</b></div>
          <div className="row"><span>Rate</span><b>{inr(q.per)} {q.unit === 'visit' ? '/visit' : '/day'}</b></div>
        </div>
      </div>

      <div className="nav-row">
        <button className="btn btn-ghost" onClick={() => (step === 1 ? nav(`/nurse/${n.id}`) : setStep(step - 1))}>
          {step === 1 ? 'Cancel' : 'Back'}
        </button>
        <button className="btn btn-gold btn-lg" disabled={!canNext} onClick={next}>
          {step === 3 ? <><CheckIcon size={16} /> Confirm booking</> : 'Continue \u2192'}
        </button>
      </div>
    </div>
  );
}
