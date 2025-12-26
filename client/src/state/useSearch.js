import { useState } from "react";
import { searchDocs } from "../api/search.api";

export function useSearch() {
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  async function handleSearch(query) {
    if (!query?.trim()) {
      setResults([]);
      return;
    }

    setSearching(true);
    const res = await searchDocs(query.trim());
    setResults(res || []);
    setSearching(false);
  }

  function clearResults() {
    setResults([]);
  }

  return {
    results,
    searching,
    handleSearch,
    clearResults,
  };
}
