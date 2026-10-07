const S = ({ size = 20, children, ...p }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor"
    strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" {...p}>{children}</svg>
);
export const SearchIcon = (p) => <S {...p}><circle cx="11" cy="11" r="7" /><path d="m16.5 16.5 4 4" /></S>;
export const CompassIcon = (p) => <S {...p}><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z" /></S>;
export const CalendarIcon = (p) => <S {...p}><rect x="3.5" y="5" width="17" height="15" rx="3" /><path d="M8 3v4M16 3v4M3.5 10h17" /></S>;
export const HeartIcon = (p) => <S {...p}><path d="M12 20s-7-4.4-7-9.4A4.1 4.1 0 0 1 12 7a4.1 4.1 0 0 1 7 3.6c0 5-7 9.4-7 9.4Z" /></S>;
export const UserIcon = (p) => <S {...p}><circle cx="12" cy="8" r="4" /><path d="M4.5 21c0-4 3.4-6.5 7.5-6.5s7.5 2.5 7.5 6.5" /></S>;
export const ShieldIcon = (p) => <S {...p}><path d="M12 2.5 4.5 5.4v5.7c0 4.8 3.2 8.2 7.5 10.4 4.3-2.2 7.5-5.6 7.5-10.4V5.4L12 2.5Z" /><path d="m9 12 2 2 4-4" /></S>;
export const CheckIcon = (p) => <S {...p}><path d="m5 13 4 4L19 7" /></S>;
export const PhoneIcon = (p) => <S {...p}><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z" /></S>;
export const PinIcon = (p) => <S {...p}><path d="M12 21s-7-4.4-7-10a7 7 0 0 1 14 0c0 5.6-7 10-7 10Z" /><circle cx="12" cy="11" r="2.4" /></S>;
export const ClockIcon = (p) => <S {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></S>;
export const BackIcon = (p) => <S {...p}><path d="M15 18l-6-6 6-6" /></S>;
export const ChevronIcon = (p) => <S {...p}><path d="m9 6 6 6-6 6" /></S>;
export const SparkIcon = (p) => <S {...p}><path d="M12 3v5M12 16v5M4.5 12h5M14.5 12h5" /><circle cx="12" cy="12" r="2.4" /></S>;
export const HomeNurseIcon = (p) => <S {...p}><path d="M3 11.5 12 4l9 7.5" /><path d="M5.5 10v9h13v-9" /><path d="M12 19v-4M10 15h4" /></S>;
