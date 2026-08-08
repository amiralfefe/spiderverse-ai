import { ChevronDown } from "lucide-react";
import { useState } from "react";
import type { GraphNode, Stats } from "../types";

const ENTITY_TYPES = ["Character", "Universe", "Event", "Team", "Work", "Power", "Concept"];

interface ExplorerFiltersProps {
  universes: GraphNode[];
  stats: Stats | null;
  selectedUniverse: string;
  onUniverseChange: (id: string) => void;
  nodeTypes: Set<string>;
  onNodeTypeToggle: (type: string) => void;
  relationshipTypes: string[];
  enabledRelationships: Set<string>;
  onRelationshipToggle: (type: string) => void;
}

export function ExplorerFilters({
  universes,
  stats,
  selectedUniverse,
  onUniverseChange,
  nodeTypes,
  onNodeTypeToggle,
  relationshipTypes,
  enabledRelationships,
  onRelationshipToggle,
}: ExplorerFiltersProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <aside className={mobileOpen ? "filter-rail mobile-open" : "filter-rail"}>
      <button
        type="button"
        className="rail-title filter-toggle"
        onClick={() => setMobileOpen((open) => !open)}
        aria-expanded={mobileOpen}
      >
        <span>Explorer</span><ChevronDown size={16} />
      </button>
      <section className="filter-section">
        <h2>Entity types</h2>
        {ENTITY_TYPES.map((type) => (
          <label key={type} className="filter-row">
            <span className={`type-marker type-${type.toLowerCase()}`} />
            <span>{type}</span>
            <input
              type="checkbox"
              checked={nodeTypes.has(type)}
              onChange={() => onNodeTypeToggle(type)}
            />
          </label>
        ))}
      </section>
      <section className="filter-section">
        <h2>Universes</h2>
        <label className={selectedUniverse === "" ? "filter-row selected" : "filter-row"}>
          <input type="radio" name="universe" checked={selectedUniverse === ""} onChange={() => onUniverseChange("")} />
          <span>All universes</span>
        </label>
        {universes.slice(0, 6).map((universe) => (
          <label key={universe.id} className={selectedUniverse === universe.id ? "filter-row selected" : "filter-row"}>
            <input
              type="radio"
              name="universe"
              checked={selectedUniverse === universe.id}
              onChange={() => onUniverseChange(universe.id)}
            />
            <span>{universe.label}</span>
          </label>
        ))}
      </section>
      <section className="filter-section relationship-filters">
        <h2>Relationships</h2>
        {relationshipTypes.slice(0, 7).map((type) => (
          <label key={type} className="filter-row">
            <input type="checkbox" checked={enabledRelationships.has(type)} onChange={() => onRelationshipToggle(type)} />
            <span>{type}</span>
          </label>
        ))}
      </section>
      {stats ? (
        <div className="rail-stats" aria-label="Graph statistics">
          <span>{stats.nodes}<small>nodes</small></span>
          <span>{stats.relationships}<small>links</small></span>
        </div>
      ) : null}
    </aside>
  );
}
