import { ArrowUpRight } from "lucide-react";
import type { GraphNode } from "../types";

interface UniverseBrowserProps {
  universes: GraphNode[];
  onSelect: (node: GraphNode) => void;
}

export function UniverseBrowser({ universes, onSelect }: UniverseBrowserProps) {
  return (
    <section className="universe-view">
      <header className="view-heading"><div><h1>Universes</h1><p>Distinct realities remain distinct nodes in the knowledge graph.</p></div><strong>{universes.length} realities</strong></header>
      <div className="universe-list">
        {universes.map((universe, index) => (
          <button key={universe.id} type="button" onClick={() => onSelect(universe)}>
            <span className="universe-index">{String(index + 1).padStart(2, "0")}</span>
            <span className="universe-orbit"><i /><i /><i /></span>
            <span className="universe-copy"><strong>{universe.label}</strong><small>Designation {universe.designation}</small><p>{universe.description}</p></span>
            <span className="universe-count"><strong>{universe.character_count ?? 0}</strong><small>characters</small></span>
            <ArrowUpRight size={18} />
          </button>
        ))}
      </div>
    </section>
  );
}
