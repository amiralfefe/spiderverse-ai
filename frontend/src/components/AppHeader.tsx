import { Search, X } from "lucide-react";
import { FormEvent, useDeferredValue, useEffect, useState } from "react";
import { api } from "../api";
import type { GraphNode, SearchMode, SearchResult } from "../types";
import { BrandMark } from "./BrandMark";

export type AppView = "explore" | "characters" | "universes" | "path" | "analytics";

const NAV_ITEMS: { id: AppView; label: string }[] = [
  { id: "explore", label: "Explore" },
  { id: "characters", label: "Characters" },
  { id: "universes", label: "Universes" },
  { id: "path", label: "Path Finder" },
  { id: "analytics", label: "Analytics" },
];

const SEARCH_MODES: { id: SearchMode; label: string }[] = [
  { id: "lexical", label: "Lexical" },
  { id: "semantic", label: "Semantic" },
  { id: "hybrid", label: "Hybrid" },
];

interface AppHeaderProps {
  view: AppView;
  onViewChange: (view: AppView) => void;
  onSelect: (node: GraphNode) => void;
}

export function AppHeader({ view, onViewChange, onSelect }: AppHeaderProps) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("hybrid");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const deferredQuery = useDeferredValue(query.trim());

  useEffect(() => {
    if (deferredQuery.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    api.search(deferredQuery, undefined, mode)
      .then((next) => {
        if (active) setResults(next);
      })
      .catch(() => {
        if (active) setResults([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [deferredQuery, mode]);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (results[0]) choose(results[0]);
  }

  function choose(node: GraphNode) {
    onSelect(node);
    onViewChange("explore");
    setQuery("");
    setOpen(false);
  }

  return (
    <header className="app-header">
      <button className="brand" type="button" onClick={() => onViewChange("explore")}>
        <BrandMark />
        <span>SPIDERVERSE <strong>AI</strong></span>
      </button>
      <nav className="primary-nav" aria-label="Primary navigation">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={view === item.id ? "nav-item active" : "nav-item"}
            onClick={() => onViewChange(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <form className="global-search" role="search" onSubmit={submit}>
        <Search size={18} aria-hidden="true" />
        <select
          className="search-mode"
          value={mode}
          onChange={(event) => {
            setMode(event.target.value as SearchMode);
            setOpen(true);
          }}
          aria-label="Search mode"
        >
          {SEARCH_MODES.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
        <input
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search the Spider-Verse…"
          aria-label="Search the Spider-Verse"
        />
        {query ? (
          <button type="button" className="clear-search" onClick={() => setQuery("")} aria-label="Clear search">
            <X size={16} />
          </button>
        ) : (
          <kbd>/</kbd>
        )}
        {open && deferredQuery.length >= 2 && (loading || results.length > 0) ? (
          <div className="search-results">
            {loading ? <p className="search-status">Searching {mode} index…</p> : null}
            {!loading ? results.slice(0, 7).map((node) => (
              <button key={node.id} type="button" onClick={() => choose(node)}>
                <span className={`type-dot type-${node.type.toLowerCase()}`} />
                <span>
                  <strong>{node.label}</strong>
                  <small>
                    {[node.type, node.aliases?.[0], node.universe_label].filter(Boolean).join(" · ")}
                  </small>
                  <small className="search-score">{node.search_mode} score: {node.score.toFixed(3)}</small>
                </span>
              </button>
            )) : null}
          </div>
        ) : null}
      </form>
    </header>
  );
}
