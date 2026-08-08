import { Search, X } from "lucide-react";
import { FormEvent, useDeferredValue, useEffect, useState } from "react";
import { api } from "../api";
import type { GraphNode } from "../types";
import { BrandMark } from "./BrandMark";

export type AppView = "explore" | "characters" | "universes" | "path";

const NAV_ITEMS: { id: AppView; label: string }[] = [
  { id: "explore", label: "Explore" },
  { id: "characters", label: "Characters" },
  { id: "universes", label: "Universes" },
  { id: "path", label: "Path Finder" },
];

interface AppHeaderProps {
  view: AppView;
  onViewChange: (view: AppView) => void;
  onSelect: (node: GraphNode) => void;
}

export function AppHeader({ view, onViewChange, onSelect }: AppHeaderProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GraphNode[]>([]);
  const [open, setOpen] = useState(false);
  const deferredQuery = useDeferredValue(query.trim());

  useEffect(() => {
    if (deferredQuery.length < 2) {
      setResults([]);
      return;
    }
    let active = true;
    api.search(deferredQuery).then((next) => {
      if (active) setResults(next);
    }).catch(() => {
      if (active) setResults([]);
    });
    return () => {
      active = false;
    };
  }, [deferredQuery]);

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
        {open && results.length > 0 ? (
          <div className="search-results">
            {results.slice(0, 7).map((node) => (
              <button key={node.id} type="button" onClick={() => choose(node)}>
                <span className={`type-dot type-${node.type.toLowerCase()}`} />
                <span><strong>{node.label}</strong><small>{node.type}</small></span>
              </button>
            ))}
          </div>
        ) : null}
      </form>
    </header>
  );
}
