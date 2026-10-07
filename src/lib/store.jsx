import { createContext, useContext, useEffect, useMemo, useRef, useState, useCallback } from 'react';

const BKEY = 'nurzing.bookings.v1';
const SKEY = 'nurzing.saved.v1';

export const STAGES = ['Requested', 'Assigned', 'En route', 'In care', 'Completed'];

const Ctx = createContext(null);
const load = (k, fallback) => { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? fallback; } catch { return fallback; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

export function BookingsProvider({ children }) {
  const [bookings, setBookings] = useState(() => load(BKEY, []));
  const [saved, setSaved] = useState(() => load(SKEY, []));
  const [toastMsg, setToastMsg] = useState('');
  const tRef = useRef(null);

  useEffect(() => save(BKEY, bookings), [bookings]);
  useEffect(() => save(SKEY, saved), [saved]);

  const toast = useCallback((msg) => {
    setToastMsg(msg);
    clearTimeout(tRef.current);
    tRef.current = setTimeout(() => setToastMsg(''), 2600);
  }, []);

  const addBooking = useCallback((b) => {
    const now = Date.now();
    const booking = {
      ...b, id: 'NZ' + String(now).slice(-7),
      statusIndex: 0,
      createdAt: now,
      stageTimes: [now],
    };
    setBookings((prev) => [booking, ...prev]);
    return booking;
  }, []);

  const advanceBooking = useCallback((id) => {
    setBookings((prev) => prev.map((b) => {
      if (b.id !== id) return b;
      const next = Math.min(b.statusIndex + 1, STAGES.length - 1);
      if (next === b.statusIndex) return b;
      return { ...b, statusIndex: next, stageTimes: [...b.stageTimes.slice(0, next), Date.now()] };
    }));
  }, []);

  const cancelBooking = useCallback((id) => {
    setBookings((prev) => prev.filter((b) => b.id !== id));
  }, []);

  const toggleSaved = useCallback((id) => {
    setSaved((prev) => {
      const on = prev.includes(id);
      toast(on ? 'Removed from saved' : 'Saved to your list');
      return on ? prev.filter((x) => x !== id) : [...prev, id];
    });
  }, [toast]);

  const value = useMemo(() => ({
    bookings, saved, toastMsg, toast, addBooking, advanceBooking, cancelBooking,
    toggleSaved, isSaved: (id) => saved.includes(id),
  }), [bookings, saved, toastMsg, toast, addBooking, advanceBooking, cancelBooking, toggleSaved]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useBookings = () => {
  const c = useContext(Ctx);
  if (!c) throw new Error('useBookings must be used inside BookingsProvider');
  return c;
};
