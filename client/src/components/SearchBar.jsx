import { useState } from "react";

export default function SearchBar({ onSearch }) {
  const [q, setQ] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const query = q.trim();
    if (!query) return;
    onSearch(query);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit} role="search">
      <input
        type="text"
        placeholder="Search documents…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        aria-label="Search documents"
      />

      <button type="submit" disabled={!q.trim()}>
        Search
      </button>
    </form>
  );
}
