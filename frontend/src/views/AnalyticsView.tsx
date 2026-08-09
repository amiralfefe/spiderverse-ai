import { Activity, GitFork, Network, Share2, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api";
import type {
  AnalyticsOverview,
  CentralityPayload,
  CentralityResult,
  CommunitiesPayload,
  GraphNode,
  SimilarityPayload,
} from "../types";

interface AnalyticsViewProps {
  characters: GraphNode[];
}

interface RankingPanelProps {
  title: string;
  description: string;
  results: CentralityResult[];
}

function percentage(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function RankingPanel({ title, description, results }: RankingPanelProps) {
  const maximum = results[0]?.score || 1;
  return (
    <section className="analytics-panel ranking-panel">
      <header>
        <div>
          <span className="analytics-kicker">Character ranking</span>
          <h2>{title}</h2>
        </div>
        <Activity size={18} aria-hidden="true" />
      </header>
      <p className="analytics-description">{description}</p>
      <ol className="ranking-list">
        {results.map((result) => (
          <li key={result.node.id}>
            <span className="ranking-position">{String(result.rank).padStart(2, "0")}</span>
            <div className="ranking-evidence">
              <div>
                <strong>{result.node.label}</strong>
                <span>{result.node.universe_id ? `${result.node.universe_id} · ` : ""}{result.degree} direct neighbors</span>
              </div>
              <div
                className="ranking-track"
                role="img"
                aria-label={`${result.node.label}: ${percentage(result.score)}`}
              >
                <i style={{ width: `${Math.max((result.score / maximum) * 100, 1)}%` }} />
              </div>
            </div>
            <code>{percentage(result.score)}</code>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function AnalyticsView({ characters }: AnalyticsViewProps) {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [degree, setDegree] = useState<CentralityPayload | null>(null);
  const [betweenness, setBetweenness] = useState<CentralityPayload | null>(null);
  const [communities, setCommunities] = useState<CommunitiesPayload | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState("miles-1610");
  const [similarity, setSimilarity] = useState<SimilarityPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [similarityLoading, setSimilarityLoading] = useState(true);
  const [error, setError] = useState("");
  const [similarityError, setSimilarityError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      api.analyticsOverview(),
      api.analyticsCentrality("degree"),
      api.analyticsCentrality("betweenness"),
      api.analyticsCommunities(),
    ])
      .then(([nextOverview, nextDegree, nextBetweenness, nextCommunities]) => {
        if (!active) return;
        setOverview(nextOverview);
        setDegree(nextDegree);
        setBetweenness(nextBetweenness);
        setCommunities(nextCommunities);
      })
      .catch((cause) => {
        if (active) {
          setError(cause instanceof Error ? cause.message : "Unable to compute graph analytics.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    setSimilarityLoading(true);
    setSimilarityError("");
    api.analyticsSimilarity(selectedCharacter)
      .then((nextSimilarity) => {
        if (active) setSimilarity(nextSimilarity);
      })
      .catch((cause) => {
        if (active) {
          setSimilarityError(
            cause instanceof Error ? cause.message : "Unable to compare character profiles.",
          );
        }
      })
      .finally(() => {
        if (active) setSimilarityLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedCharacter]);

  return (
    <main className="analytics-view">
      <header className="view-heading analytics-heading">
        <div>
          <h1>Graph Analytics</h1>
          <p>Deterministic structural signals computed from the V1 knowledge graph.</p>
        </div>
        <strong>Phase 5</strong>
      </header>

      {error ? <div className="analytics-error" role="alert">{error}</div> : null}
      {loading ? <div className="analytics-loading">Computing centralities and communities…</div> : null}

      {overview ? (
        <section className="analytics-overview" aria-label="Graph overview">
          <article><Network size={18} /><span>Unique connections</span><strong>{overview.unique_connections}</strong></article>
          <article><Share2 size={18} /><span>Average degree</span><strong>{overview.average_degree.toFixed(2)}</strong></article>
          <article><GitFork size={18} /><span>Components</span><strong>{overview.connected_components}</strong></article>
          <article><Users size={18} /><span>Communities</span><strong>{overview.communities}</strong></article>
        </section>
      ) : null}

      {degree && betweenness ? (
        <div className="analytics-rankings">
          <RankingPanel
            title="Degree centrality"
            description="Who connects directly to the broadest set of unique graph neighbors."
            results={degree.results}
          />
          <RankingPanel
            title="Betweenness centrality"
            description="Who most often sits on shortest routes between otherwise distant entities."
            results={betweenness.results}
          />
        </div>
      ) : null}

      {communities ? (
        <section className="analytics-section">
          <header className="analytics-section-heading">
            <div>
              <span className="analytics-kicker">Emergent structure</span>
              <h2>Graph communities</h2>
              <p>Greedy modularity found {communities.total_count} groups; {communities.count} contain at least two entities.</p>
            </div>
            <code>Q {communities.modularity.toFixed(4)}</code>
          </header>
          <div className="community-grid">
            {communities.communities.map((community) => (
              <article key={community.id} className="community-card">
                <header><strong>{community.id.replace("community-", "Cluster ")}</strong><span>{community.size} entities</span></header>
                <p>{Object.entries(community.member_types).map(([type, count]) => `${count} ${type}`).join(" · ")}</p>
                <div className="community-members">
                  {community.members.slice(0, 10).map((member) => (
                    <span key={member.id} className={`type-${member.type.toLowerCase()}`}>{member.label}</span>
                  ))}
                  {community.members.length > 10 ? <span>+{community.members.length - 10} more</span> : null}
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="analytics-section similarity-section">
        <header className="analytics-section-heading">
          <div>
            <span className="analytics-kicker">Structural similarity</span>
            <h2>Closest character profiles</h2>
            <p>Jaccard overlap between each character&apos;s direct graph neighbors.</p>
          </div>
          <label>
            <span>Compare character</span>
            <select value={selectedCharacter} onChange={(event) => setSelectedCharacter(event.target.value)}>
              {characters.map((character) => <option key={character.id} value={character.id}>{character.label} · {character.universe_id}</option>)}
            </select>
          </label>
        </header>
        {similarityError ? <div className="analytics-error" role="alert">{similarityError}</div> : null}
        {similarityLoading ? <div className="analytics-loading">Comparing neighborhoods…</div> : null}
        {!similarityLoading && similarity ? (
          <ol className="similarity-list">
            {similarity.results.map((result, index) => (
              <li key={result.node.id}>
                <span className="ranking-position">{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <strong>{result.node.label}<small>{result.node.universe_id}</small></strong>
                  <p>{result.shared_neighbors.length > 0 ? result.shared_neighbors.map((node) => node.label).join(" · ") : "No shared direct neighbor"}</p>
                </div>
                <span>{result.shared_neighbor_count} shared</span>
                <code>{percentage(result.score)}</code>
              </li>
            ))}
          </ol>
        ) : null}
      </section>

      <p className="analytics-caveat">
        Scores use an undirected simple projection: parallel relations count once per connected pair. They describe this demonstration dataset, not Marvel canon or narrative importance.
      </p>
    </main>
  );
}
