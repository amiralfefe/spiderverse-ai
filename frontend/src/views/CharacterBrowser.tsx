import { Search } from "lucide-react";
import { useDeferredValue, useMemo, useState } from "react";
import type { GraphNode } from "../types";

interface CharacterBrowserProps {
  characters: GraphNode[];
  universes: GraphNode[];
  onSelect: (node: GraphNode) => void;
}

export function CharacterBrowser({ characters, universes, onSelect }: CharacterBrowserProps) {
  const [query, setQuery] = useState("");
  const [universe, setUniverse] = useState("");
  const deferredQuery = useDeferredValue(query.toLowerCase());
  const filtered = useMemo(() => characters.filter((character) => {
    const matchesQuery = !deferredQuery || `${character.label} ${(character.aliases ?? []).join(" ")}`.toLowerCase().includes(deferredQuery);
    return matchesQuery && (!universe || character.universe_id === universe);
  }), [characters, deferredQuery, universe]);
  const universeMap = useMemo(() => new Map(universes.map((item) => [item.id, item.label])), [universes]);

  return (
    <section className="catalog-view">
      <header className="view-heading"><div><h1>Characters</h1><p>Search identities without collapsing their multiverse variants.</p></div><strong>{filtered.length} entities</strong></header>
      <div className="catalog-controls">
        <label><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search characters and aliases…" /></label>
        <select value={universe} onChange={(event) => setUniverse(event.target.value)} aria-label="Filter characters by universe">
          <option value="">All universes</option>
          {universes.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
        </select>
      </div>
      <div className="entity-table" role="list">
        {filtered.map((character) => (
          <button key={character.id} type="button" role="listitem" onClick={() => onSelect(character)}>
            <span className="entity-symbol type-character">{character.label.slice(0, 1)}</span>
            <span className="entity-main"><strong>{character.label}</strong><small>{character.aliases?.join(" · ") ?? "Character"}</small></span>
            <span>{universeMap.get(character.universe_id ?? "") ?? "Unknown universe"}</span>
            <span className="row-action">Explore →</span>
          </button>
        ))}
      </div>
    </section>
  );
}
