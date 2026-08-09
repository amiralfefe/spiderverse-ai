import type {
  AnalyticsOverview,
  AskResponse,
  CharacterDetail,
  CentralityPayload,
  CommunitiesPayload,
  GraphNode,
  GraphPayload,
  PathPayload,
  SimilarityPayload,
  Stats,
} from "./types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? "The graph service returned an error.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  stats: () => request<Stats>("/api/stats"),
  universes: () => request<GraphNode[]>("/api/universes"),
  characters: (universeId?: string) => {
    const query = universeId ? `?universe_id=${encodeURIComponent(universeId)}` : "";
    return request<GraphNode[]>(`/api/characters${query}`);
  },
  search: (query: string, nodeType?: string) => {
    const params = new URLSearchParams({ q: query });
    if (nodeType) params.set("node_type", nodeType);
    return request<GraphNode[]>(`/api/search?${params}`);
  },
  character: (id: string) => request<CharacterDetail>(`/api/characters/${id}`),
  graph: (focusId: string, universeId?: string, depth = 1) => {
    const params = new URLSearchParams({ focus_id: focusId, depth: String(depth), limit: "100" });
    if (universeId) params.set("universe_id", universeId);
    return request<GraphPayload>(`/api/graph?${params}`);
  },
  path: (startId: string, endId: string) => {
    const params = new URLSearchParams({ start_id: startId, end_id: endId });
    return request<PathPayload>(`/api/path?${params}`);
  },
  ask: (question: string) =>
    request<AskResponse>("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
  analyticsOverview: () => request<AnalyticsOverview>("/api/analytics/overview"),
  analyticsCentrality: (
    metric: "degree" | "betweenness",
    nodeType = "Character",
    limit = 10,
  ) => {
    const params = new URLSearchParams({
      metric,
      node_type: nodeType,
      limit: String(limit),
    });
    return request<CentralityPayload>(`/api/analytics/centrality?${params}`);
  },
  analyticsCommunities: (minSize = 2) =>
    request<CommunitiesPayload>(`/api/analytics/communities?min_size=${minSize}`),
  analyticsSimilarity: (characterId: string, limit = 10) =>
    request<SimilarityPayload>(
      `/api/analytics/similarity/${encodeURIComponent(characterId)}?limit=${limit}`,
    ),
};
