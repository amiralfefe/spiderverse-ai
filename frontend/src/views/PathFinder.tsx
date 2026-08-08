import { ArrowRight, Route } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import type { GraphNode, PathPayload } from "../types";

interface PathFinderProps {
  characters: GraphNode[];
  onPathFound: (path: PathPayload) => void;
}

export function PathFinder({ characters, onPathFound }: PathFinderProps) {
  const [startId, setStartId] = useState("miles-1610");
  const [endId, setEndId] = useState("daredevil-616");
  const [path, setPath] = useState<PathPayload | null>(null);
  const [loading, setLoading] = useState(false);

  async function findPath() {
    if (!startId || !endId || startId === endId) return;
    setLoading(true);
    try {
      const result = await api.path(startId, endId);
      setPath(result);
      if (result.found) onPathFound(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="path-view">
      <header className="view-heading"><div><h1>Path Finder</h1><p>Reveal the shortest explainable route between two characters.</p></div><Route size={28} /></header>
      <div className="path-form">
        <label><span>Character A</span><select value={startId} onChange={(event) => setStartId(event.target.value)}>{characters.map((character) => <option key={character.id} value={character.id}>{character.label} — {character.universe_id}</option>)}</select></label>
        <ArrowRight size={24} />
        <label><span>Character B</span><select value={endId} onChange={(event) => setEndId(event.target.value)}>{characters.map((character) => <option key={character.id} value={character.id}>{character.label} — {character.universe_id}</option>)}</select></label>
        <button type="button" onClick={findPath} disabled={loading || startId === endId}>{loading ? "Searching…" : "Find path"}</button>
      </div>
      <div className="path-result">
        {path?.found ? (
          <><div className="path-summary"><strong>{path.hops} hops</strong><span>Graph-backed shortest path</span></div><div className="path-chain">{path.nodes.map((node, index) => <div key={node.id}>{index > 0 ? <span className="path-edge"><i>{path.edges[index - 1]?.type}</i><ArrowRight size={18} /></span> : null}<button type="button"><span className={`entity-symbol type-${node.type.toLowerCase()}`}>{node.label.slice(0, 1)}</span><strong>{node.label}</strong><small>{node.type}</small></button></div>)}</div></>
        ) : path ? <div className="empty-path"><Route size={24} /><p>No narrative path is present in the current demonstration seed.</p></div> : <div className="empty-path"><Route size={24} /><p>Select two characters to traverse allies, families, variants, teams, and events.</p></div>}
      </div>
    </section>
  );
}
