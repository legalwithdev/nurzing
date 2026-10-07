export const CARE_TYPES = ['Home Nursing', 'Elderly Care', 'Post-Surgical', 'Mother & Baby', 'Physiotherapy', 'ICU-trained'];

export const CARE_ICON = {
  'Home Nursing': 'M3 11.5 12 4l9 7.5M5.5 10v9h13v-9M10 19v-5h4v5',
  'Elderly Care': 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM5 21c0-3.9 3.1-7 7-7s7 3.1 7 7',
  'Post-Surgical': 'M12 3v18M3 12h18',
  'Mother & Baby': 'M12 21s-7-4.3-7-10a7 7 0 0 1 14 0c0 5.7-7 10-7 10Z',
  'Physiotherapy': 'M4 20 9 15l3 3 7-8M14 6l3-2 3 3',
  'ICU-trained': 'M3 12h4l2-5 3 10 2-5h7',
};

export const SHIFTS = [
  { id: 'day12', label: '12-hour day', sub: 'Daytime cover', mult: 1, unit: 'day' },
  { id: 'night', label: 'Night shift', sub: 'Overnight cover', mult: 1.15, unit: 'day' },
  { id: 'live24', label: '24-hour live-in', sub: 'Round the clock', mult: 1.8, unit: 'day' },
  { id: 'hourly', label: 'Hourly visit', sub: 'Short, skilled visit', mult: 0.35, unit: 'visit' },
];

const PREMIUM = { 'Home Nursing': 1, 'Elderly Care': 0.9, 'Post-Surgical': 1.15, 'Mother & Baby': 1.2, 'Physiotherapy': 0.8, 'ICU-trained': 1.45 };

export function quote(nurse, careType, shiftId, days = 1) {
  const shift = SHIFTS.find((s) => s.id === shiftId) || SHIFTS[0];
  const prem = PREMIUM[careType] || 1;
  const daily = Math.round(nurse.rate * prem);
  const per = Math.round(daily * shift.mult);
  const total = shift.unit === 'visit' ? per : per * days;
  return { daily, per, total, unit: shift.unit, shift, days: shift.unit === 'visit' ? 1 : days };
}

export const inr = (n) => '\u20B9' + Number(n || 0).toLocaleString('en-IN');
