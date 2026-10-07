export default function Stars({ rating = 0, count, size = 13 }) {
  const full = Math.round(rating);
  return (
    <span className="stars" style={{ fontSize: size }} aria-label={`${rating} out of 5`}>
      {'\u2605'.repeat(full)}{'\u2606'.repeat(Math.max(0, 5 - full))}
      <b>{rating}{count != null ? ` \u00B7 ${count}` : ''}</b>
    </span>
  );
}
