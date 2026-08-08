import { CheckCircle2, ChevronDown, CircleAlert, ExternalLink, Network, RotateCcw } from "lucide-react";
import type { CharacterDetail, GraphNode, RelationDetail, Source } from "../types";

interface EntityInspectorProps {
  node: GraphNode | null;
  detail: CharacterDetail | null;
  loading: boolean;
  onExplore: (node: GraphNode) => void;
}

function relationRows(detail: CharacterDetail): RelationDetail[] {
  return detail.relations.filter((item) => !["HAS_POWER", "APPEARS_IN", "BELONGS_TO_UNIVERSE"].includes(item.edge.type));
}

function SourceRow({ source }: { source: Source }) {
  return (
    <div className="source-row">
      {source.verified ? <CheckCircle2 size={16} /> : <CircleAlert size={16} />}
      <span><strong>{source.source_title}</strong><small>{source.verified ? "Curated work evidence" : "Unverified demo evidence"}</small></span>
      {source.source_url ? <ExternalLink size={14} /> : null}
    </div>
  );
}

export function EntityInspector({ node, detail, loading, onExplore }: EntityInspectorProps) {
  if (!node) {
    return (
      <aside className="entity-inspector empty-inspector">
        <Network size={24} />
        <h2>Select an entity</h2>
        <p>Choose a node to inspect its graph-backed properties and evidence.</p>
      </aside>
    );
  }
  const sources = detail?.sources ?? [];
  const relations = detail ? relationRows(detail) : [];
  return (
    <aside className="entity-inspector">
      <div className="rail-title"><span>Selected entity</span><ChevronDown size={16} /></div>
      <div className="entity-heading">
        <span className={`entity-symbol type-${node.type.toLowerCase()}`}>{node.label.slice(0, 1)}</span>
        <div><h2>{node.label}</h2><p>{node.aliases?.[0] ?? node.type}</p></div>
      </div>
      {detail?.universe ? <span className="universe-label">◎ {detail.universe.label.toUpperCase()}</span> : null}
      <button type="button" className="explore-entity" onClick={() => onExplore(node)}><RotateCcw size={14} /> Explore from here</button>
      <section className="inspector-section">
        <h3>Overview</h3>
        <dl>
          <div><dt>Type</dt><dd>{node.type}</dd></div>
          {detail?.universe ? <div><dt>Universe</dt><dd>{detail.universe.label}</dd></div> : null}
          {node.aliases?.length ? <div><dt>Aliases</dt><dd>{node.aliases.join(", ")}</dd></div> : null}
          {node.designation ? <div><dt>Designation</dt><dd>{node.designation}</dd></div> : null}
        </dl>
        <p className="entity-description">{node.description ?? "No description in the current graph seed."}</p>
      </section>
      {loading ? <div className="loading-line">Retrieving graph facts…</div> : null}
      {detail && detail.powers.length > 0 ? (
        <section className="inspector-section">
          <h3>Powers</h3>
          <ul className="plain-list">{detail.powers.slice(0, 5).map((power) => <li key={power.id}>{power.label}</li>)}</ul>
        </section>
      ) : null}
      {relations.length > 0 ? (
        <section className="inspector-section">
          <h3>Connections <span>{relations.length}</span></h3>
          <div className="connection-list">
            {relations.slice(0, 7).map((item) => (
              <button key={item.edge.id} type="button" onClick={() => onExplore(item.node)}>
                <span className={`type-dot type-${item.node.type.toLowerCase()}`} />
                <strong>{item.node.label}</strong>
                <small>{item.edge.type}</small>
              </button>
            ))}
          </div>
        </section>
      ) : null}
      {detail && detail.works.length > 0 ? (
        <section className="inspector-section">
          <h3>Appearances</h3>
          <p className="section-summary">{detail.works.length} works in this demonstration seed.</p>
        </section>
      ) : null}
      {sources.length > 0 ? (
        <section className="inspector-section">
          <h3>Sources</h3>
          <div className="source-list">{sources.slice(0, 3).map((source) => <SourceRow key={`${source.source_title}-${source.source_type}`} source={source} />)}</div>
        </section>
      ) : null}
    </aside>
  );
}
