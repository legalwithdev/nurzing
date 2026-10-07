import { Routes, Route } from 'react-router-dom';
import AppShell from './components/AppShell.jsx';
import Discover from './pages/Discover.jsx';
import NurseProfile from './pages/NurseProfile.jsx';
import BookingFlow from './pages/BookingFlow.jsx';
import Bookings from './pages/Bookings.jsx';
import Saved from './pages/Saved.jsx';
import Account from './pages/Account.jsx';

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Discover />} />
        <Route path="/nurse/:id" element={<NurseProfile />} />
        <Route path="/book/:id" element={<BookingFlow />} />
        <Route path="/bookings" element={<Bookings />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/account" element={<Account />} />
        <Route path="*" element={<Discover />} />
      </Route>
    </Routes>
  );
}
