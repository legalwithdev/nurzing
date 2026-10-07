// SAMPLE DATA ONLY — every name, role, rating, review, distance and rate below is invented
// for demo purposes. Replace with your real, verified professional records before launch.
export const CITIES = ['Bengaluru', 'Mumbai', 'Delhi NCR', 'Pune', 'Hyderabad', 'Chennai'];

const V = (extra = {}) => ({ id: true, police: true, insured: true, vaccinated: true, ...extra });

export const NURSES = [
  { id: 'nz-101', name: 'Ananya Rao', role: 'Senior Staff Nurse', city: 'Bengaluru', area: 'Koramangala', rate: 1800, rating: 4.9, reviews: 214, years: 8, availableToday: true, distanceKm: 2.4,
    careTypes: ['Home Nursing', 'ICU-trained', 'Post-Surgical'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Kannada'], skills: ['Ventilator care', 'Tracheostomy', 'IV & injections', 'Wound dressing'],
    verified: V(), about: 'ICU-trained nurse with 8 years across hospital critical care and home ICU setups. Calm with families and meticulous with medication schedules.',
    reviewsList: [
      { name: 'Sneha I.', role: 'Daughter', stars: 5, when: '2 weeks ago', text: 'Papa ki surgery ke baad night cover diya. Extremely skilled and reassuring.' },
      { name: 'Arjun M.', role: 'Son', stars: 5, when: '1 month ago', text: 'Handled a complex catheter case at home without any fuss. Highly recommend.' },
    ] },
  { id: 'nz-102', name: 'Fatima Sheikh', role: 'Maternity Nurse', city: 'Bengaluru', area: 'Whitefield', rate: 2000, rating: 5.0, reviews: 168, years: 6, availableToday: true, distanceKm: 5.1,
    careTypes: ['Mother & Baby', 'Home Nursing'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Urdu'], skills: ['Newborn care', 'Lactation support', 'Post-partum care', 'Sleep routines'],
    verified: V(), about: 'Specialises in newborn and post-partum care. Gentle, patient and brilliant with first-time parents.',
    reviewsList: [
      { name: 'Aisha K.', role: 'New mother', stars: 5, when: '3 weeks ago', text: 'As a first-time mum I was terrified. She was calm, skilled and genuinely kind.' },
    ] },
  { id: 'nz-103', name: 'Rakesh Nair', role: 'Attendant / Caregiver', city: 'Mumbai', area: 'Andheri West', rate: 1100, rating: 4.7, reviews: 302, years: 10, availableToday: true, distanceKm: 3.8,
    careTypes: ['Elderly Care'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Marathi'], skills: ['Mobility support', 'Hygiene & feeding', 'Companionship', 'Fall prevention'],
    verified: V({ vaccinated: true }), about: 'A decade of elderly companionship and daily-living support. Strong, dependable and very patient with dementia care.',
    reviewsList: [
      { name: 'Rahul M.', role: 'Son', stars: 5, when: '1 week ago', text: 'Became part of the family. My father looks forward to his shifts.' },
      { name: 'Neha S.', role: 'Daughter', stars: 4, when: '2 months ago', text: 'Very reliable. Occasional timing changes but always informed in advance.' },
    ] },
  { id: 'nz-104', name: 'Meera Krishnan', role: 'Physiotherapist', city: 'Chennai', area: 'Adyar', rate: 900, rating: 4.8, reviews: 141, years: 7, availableToday: false, distanceKm: 4.2,
    careTypes: ['Physiotherapy'], shifts: ['hourly', 'day12'],
    languages: ['English', 'Tamil'], skills: ['Post-surgery rehab', 'Stroke recovery', 'Pain management', 'Mobility'],
    verified: V({ police: true }), about: 'Licensed physiotherapist focused on post-surgical and neuro rehab at home, with structured weekly progress plans.',
    reviewsList: [
      { name: 'Vikram R.', role: 'Patient', stars: 5, when: '3 weeks ago', text: 'After knee replacement, walking again in six weeks. Clear plan every session.' },
    ] },
  { id: 'nz-105', name: 'Priya Deshmukh', role: 'Staff Nurse', city: 'Pune', area: 'Baner', rate: 1500, rating: 4.9, reviews: 97, years: 5, availableToday: true, distanceKm: 1.9,
    careTypes: ['Home Nursing', 'Post-Surgical'], shifts: ['day12', 'night'],
    languages: ['English', 'Hindi', 'Marathi'], skills: ['Medication management', 'Vitals monitoring', 'Drain care', 'Doctor coordination'],
    verified: V(), about: 'Organised and communicative, Priya keeps doctors, families and medication charts perfectly in sync.',
    reviewsList: [
      { name: 'Sanjay P.', role: 'Husband', stars: 5, when: '5 days ago', text: 'Kept a flawless medication log and flagged an interaction early. Excellent.' },
    ] },
  { id: 'nz-106', name: 'Imran Qureshi', role: 'ICU-trained Nurse', city: 'Delhi NCR', area: 'Saket', rate: 2300, rating: 4.8, reviews: 76, years: 9, availableToday: true, distanceKm: 6.3,
    careTypes: ['ICU-trained', 'Home Nursing', 'Post-Surgical'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi'], skills: ['Ventilator care', 'Suctioning', 'Catheter care', 'Critical monitoring'],
    verified: V(), about: 'Nine years in critical care. Comfortable setting up and running home ICU support with tight monitoring.',
    reviewsList: [
      { name: 'Deepa N.', role: 'Daughter', stars: 5, when: '1 month ago', text: 'Took over a ventilator case at home with total confidence. A lifesaver.' },
    ] },
  { id: 'nz-107', name: 'Lakshmi Reddy', role: 'Elderly Care Nurse', city: 'Hyderabad', area: 'Gachibowli', rate: 1300, rating: 4.9, reviews: 188, years: 6, availableToday: true, distanceKm: 2.7,
    careTypes: ['Elderly Care', 'Home Nursing'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Telugu', 'Hindi'], skills: ['Diabetes care', 'BP monitoring', 'Mobility support', 'Nutrition planning'],
    verified: V(), about: 'Warm and disciplined, Lakshmi manages chronic conditions in seniors with careful daily routines.',
    reviewsList: [
      { name: 'Kavya B.', role: 'Daughter', stars: 5, when: '2 weeks ago', text: 'Ammamma ke BP aur sugar dono track pe. Very caring.' },
    ] },
  { id: 'nz-108', name: 'Grace Fernandes', role: 'Senior Staff Nurse', city: 'Mumbai', area: 'Bandra', rate: 1900, rating: 4.7, reviews: 122, years: 11, availableToday: false, distanceKm: 7.4,
    careTypes: ['Home Nursing', 'Post-Surgical', 'Mother & Baby'], shifts: ['day12', 'night'],
    languages: ['English', 'Hindi', 'Marathi', 'Konkani'], skills: ['Post-op care', 'Palliative support', 'Wound care', 'Family training'],
    verified: V(), about: 'Eleven years of bedside experience including palliative care. Teaches families to manage care confidently.',
    reviewsList: [
      { name: 'Nikhil D.', role: 'Son', stars: 5, when: '3 weeks ago', text: 'Compassionate palliative care for my mother. We felt supported throughout.' },
    ] },
  { id: 'nz-109', name: 'Karan Singh', role: 'Attendant / Ward Boy', city: 'Delhi NCR', area: 'Dwarka', rate: 1000, rating: 4.6, reviews: 265, years: 8, availableToday: true, distanceKm: 5.6,
    careTypes: ['Elderly Care'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Punjabi'], skills: ['Lifting & transfers', 'Hygiene support', 'Feeding', 'Night watch'],
    verified: V({ police: true }), about: 'Physically strong and gentle, Karan handles transfers and night watch for bedridden patients.',
    reviewsList: [
      { name: 'Pooja V.', role: 'Daughter', stars: 5, when: '1 week ago', text: 'Reliable for transfers and night duty. Very respectful.' },
    ] },
  { id: 'nz-110', name: 'Divya Pillai', role: 'Staff Nurse', city: 'Chennai', area: 'Velachery', rate: 1600, rating: 4.9, reviews: 88, years: 5, availableToday: true, distanceKm: 3.1,
    careTypes: ['Home Nursing', 'Post-Surgical'], shifts: ['day12', 'night'],
    languages: ['English', 'Tamil', 'Hindi'], skills: ['IV & injections', 'Wound dressing', 'Vitals', 'Post-op care'],
    verified: V(), about: 'Quick, precise and reassuring. Divya is a favourite for post-operative home recovery.',
    reviewsList: [
      { name: 'Hari K.', role: 'Patient', stars: 5, when: '2 weeks ago', text: 'Dressing changes were painless and on time every day.' },
    ] },
  { id: 'nz-111', name: 'Sunita Joshi', role: 'Maternity Nurse', city: 'Pune', area: 'Kothrud', rate: 1900, rating: 4.8, reviews: 103, years: 7, availableToday: true, distanceKm: 2.2,
    careTypes: ['Mother & Baby', 'Home Nursing'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Marathi'], skills: ['Newborn care', 'Lactation support', 'Sleep routines', 'Post-partum'],
    verified: V(), about: 'Experienced with twins and premature newborns. Calm hands, clear guidance for new parents.',
    reviewsList: [
      { name: 'Megha T.', role: 'New mother', stars: 5, when: '1 month ago', text: 'Twins handle karna mushkil tha — she made it look easy.' },
    ] },
  { id: 'nz-112', name: 'Joseph Mathew', role: 'Senior Staff Nurse', city: 'Bengaluru', area: 'Indiranagar', rate: 1700, rating: 4.9, reviews: 149, years: 10, availableToday: true, distanceKm: 1.6,
    careTypes: ['Home Nursing', 'ICU-trained', 'Post-Surgical'], shifts: ['day12', 'night', 'live24'],
    languages: ['English', 'Hindi', 'Malayalam', 'Kannada'], skills: ['Critical monitoring', 'Wound care', 'Medication', 'Emergency response'],
    verified: V(), about: 'Ten years across ICU and home care. Steady in emergencies and excellent at family communication.',
    reviewsList: [
      { name: 'Anita S.', role: 'Daughter', stars: 5, when: '3 days ago', text: 'Handled a sudden dip calmly and coordinated with the doctor instantly.' },
    ] },
];

export const getNurse = (id) => NURSES.find((n) => n.id === id);
