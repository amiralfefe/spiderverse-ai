import { RotateCcw } from "lucide-react";
import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { AppHeader, type AppView } from "./components/AppHeader";
import { AskBar } from "./components/AskBar";
import { EntityInspector } from "./components/EntityInspector";
import { ExplorerFilters } from "./components/ExplorerFilters";
import type { CharacterDetail, GraphNode, GraphPayload, PathPayload, Stats } from "./types";
import { CharacterBrowser } from "./views/CharacterBrowser";
import { PathFinder } from "./views/PathFinder";
import { UniverseBrowser } from "./views/UniverseBrowser";

const INITIAL_NODE_TYPES = new Set(["Character", "Universe", "Event", "Team", "Concept"]);
const DEFAULT_RELATIONSHIPS = new Set([
  "ALLY_OF",
  "BELONGS_TO_UNIVERSE",
  "CONFLICT_WITH",
  "MEMBER_OF",
  "MENTORED_BY",
  "PARTICIPATED_IN",
]);
const GraphCanvas = lazy(() =>
  import("./components/GraphCanvas").then((module) => ({ default: module.GraphCanvas })),
);
const AnalyticsView = lazy(() =>
  import("./views/AnalyticsView").then((module) => ({ default: module.AnalyticsView })),
);

export default function App() {
  const [view, setView] = useState<AppView>("explore");
  const [stats, setStats] = useState<Stats | null>(null);
  const [universes, setUniverses] = useState<GraphNode[]>([]);
  const [characters, setCharacters] = useState<GraphNode[]>([]);
  const [graph, setGraph] = useState<GraphPayload>({ nodes: [], edges: [], focus_id: "miles-1610" });
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [detail, setDetail] = useState<CharacterDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingGraph, setLoadingGraph] = useState(true);
  const [error, setError] = useState("");
  const [selectedUniverse, setSelectedUniverse] = useState("");
  const [nodeTypes, setNodeTypes] = useState(() => new Set(INITIAL_NODE_TYPES));
  const [enabledRelationships, setEnabledRelationships] = useState<Set<string>>(new Set());

  const loadNode = useCallback(async (node: GraphNode, universeId = "") => {
    setSelected(node);
    setError("");
    setLoadingGraph(true);
    setLoadingDetail(node.type === "Character");
    try {
      const requests: [Promise<GraphPayload>, Promise<CharacterDetail | null>] = [
        api.graph(node.id, universeId || undefined),
        node.type === "Character" ? api.character(node.id) : Promise.resolve(null),
      ];
      const [nextGraph, nextDetail] = await Promise.all(requests);
      setGraph(nextGraph);
      setDetail(nextDetail);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to retrieve graph data.");
    } finally {
      setLoadingGraph(false);
      setLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    Promise.all([api.stats(), api.universes(), api.characters(), api.search("Miles Morales", "Character")])
      .then(async ([nextStats, nextUniverses, nextCharacters, miles]) => {
        if (!active) return;
        setStats(nextStats);
        setUniverses(nextUniverses);
        setCharacters(nextCharacters);
        if (miles[0]) await loadNode(miles[0]);
      })
      .catch((cause) => {
        if (active) setError(cause instanceof Error ? cause.message : "Unable to start the explorer.");
      });
    return () => { active = false; };
  }, [loadNode]);

  const relationshipTypes = useMemo(() => [...new Set(graph.edges.map((edge) => edge.type))].sort(), [graph.edges]);
  useEffect(() => {
    setEnabledRelationships(
      new Set(relationshipTypes.filter((type) => DEFAULT_RELATIONSHIPS.has(type))),
    );
  }, [relationshipTypes]);

  const visibleGraph = useMemo<GraphPayload>(() => {
    const typedNodes = graph.nodes.filter((node) => nodeTypes.has(node.type));
    const typedIds = new Set(typedNodes.map((node) => node.id));
    const edges = graph.edges.filter(
      (edge) =>
        typedIds.has(edge.source) &&
        typedIds.has(edge.target) &&
        enabledRelationships.has(edge.type),
    );
    const connectedIds = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
    const nodes = typedNodes.filter(
      (node) => node.id === graph.focus_id || connectedIds.has(node.id),
    );
    return { nodes, edges, focus_id: graph.focus_id };
  }, [enabledRelationships, graph, nodeTypes]);

  const handleNodeSelect = useCallback((node: GraphNode) => {
    void loadNode(node, selectedUniverse);
  }, [loadNode, selectedUniverse]);

  function handleUniverseChange(universeId: string) {
    setSelectedUniverse(universeId);
    if (selected) void loadNode(selected, universeId);
  }

  function toggleSet(value: string, setter: React.Dispatch<React.SetStateAction<Set<string>>>) {
    setter((current) => {
      const next = new Set(current);
      if (next.has(value)) next.delete(value); else next.add(value);
      return next;
    });
  }

  function showExplore(node: GraphNode) {
    setView("explore");
    void loadNode(node);
  }

  function showPath(path: PathPayload) {
    setGraph({ nodes: path.nodes, edges: path.edges, focus_id: path.nodes[0]?.id ?? null });
  }

  const handleAskGraphResult = useCallback((next: GraphPayload) => {
    const focus = next.nodes.find((node) => node.id === next.focus_id) ?? next.nodes[0] ?? null;
    setGraph(next);
    setSelected(focus);
    setDetail(null);
    setError("");
    if (focus?.type !== "Character") {
      setLoadingDetail(false);
      return;
    }
    setLoadingDetail(true);
    api.character(focus.id)
      .then(setDetail)
      .catch((cause) => {
        setError(cause instanceof Error ? cause.message : "Unable to retrieve graph data.");
      })
      .finally(() => setLoadingDetail(false));
  }, []);

  return (
    <div className="app-shell">
      <AppHeader view={view} onViewChange={setView} onSelect={showExplore} />
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {view === "explore" ? (
        <main className="explorer-layout">
          <ExplorerFilters
            universes={universes}
            stats={stats}
            selectedUniverse={selectedUniverse}
            onUniverseChange={handleUniverseChange}
            nodeTypes={nodeTypes}
            onNodeTypeToggle={(type) => toggleSet(type, setNodeTypes)}
            relationshipTypes={relationshipTypes}
            enabledRelationships={enabledRelationships}
            onRelationshipToggle={(type) => toggleSet(type, setEnabledRelationships)}
          />
          <section className="graph-workspace">
            <header className="workspace-toolbar">
              <div><h1>Knowledge Graph</h1><p>{selected ? `Focused on ${selected.label}` : "Structured multiverse explorer"}</p></div>
              <div className="toolbar-controls">
                <select value={selectedUniverse} onChange={(event) => handleUniverseChange(event.target.value)} aria-label="Universe filter">
                  <option value="">All universes</option>
                  {universes.map((universe) => <option key={universe.id} value={universe.id}>{universe.label}</option>)}
                </select>
                <span>{enabledRelationships.size || "No"} relationships</span>
                <button type="button" onClick={() => selected && loadNode(selected, selectedUniverse)}><RotateCcw size={15} /> Reset view</button>
              </div>
            </header>
            {loadingGraph && graph.nodes.length === 0 ? <div className="canvas-loading">Building the neighborhood…</div> : (
              <Suspense fallback={<div className="canvas-loading">Loading graph renderer…</div>}>
                <GraphCanvas
                  nodes={visibleGraph.nodes}
                  edges={visibleGraph.edges}
                  focusId={visibleGraph.focus_id}
                  selectedId={selected?.id ?? null}
                  onSelect={handleNodeSelect}
                />
              </Suspense>
            )}
            <AskBar onGraphResult={handleAskGraphResult} />
          </section>
          <EntityInspector
            node={selected}
            detail={detail?.character.id === selected?.id ? detail : null}
            loading={loadingDetail}
            onExplore={handleNodeSelect}
          />
        </main>
      ) : null}
      {view === "characters" ? <CharacterBrowser characters={characters} universes={universes} onSelect={showExplore} /> : null}
      {view === "universes" ? <UniverseBrowser universes={universes} onSelect={showExplore} /> : null}
      {view === "path" ? <PathFinder characters={characters} onPathFound={showPath} /> : null}
      {view === "analytics" ? (
        <Suspense fallback={<div className="canvas-loading">Computing graph analytics…</div>}>
          <AnalyticsView characters={characters} />
        </Suspense>
      ) : null}
    </div>
  );
}
