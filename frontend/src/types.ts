export type NodeType =
  | "Character"
  | "Universe"
  | "Work"
  | "Event"
  | "Team"
  | "Power"
  | "Concept";

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  description?: string;
  universe_id?: string;
  designation?: string;
  aliases?: string[];
  status?: string;
  character_count?: number;
  work_type?: string;
  [key: string]: unknown;
}

export interface Source {
  source_title: string;
  source_type: string;
  source_url?: string;
  verified: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Source & Record<string, unknown>;
}

export interface GraphPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
  focus_id: string | null;
}

export interface RelationDetail {
  edge: GraphEdge;
  node: GraphNode;
  direction: "outgoing" | "incoming";
}

export interface CharacterDetail {
  character: GraphNode;
  universe: GraphNode | null;
  powers: GraphNode[];
  works: GraphNode[];
  relations: RelationDetail[];
  sources: Source[];
}

export interface Stats {
  nodes: number;
  relationships: number;
  by_type: Record<string, number>;
  verified_relationships: number;
  demo_relationships: number;
}

export interface PathPayload {
  found: boolean;
  nodes: GraphNode[];
  edges: GraphEdge[];
  hops: number | null;
}

export interface AskResponse {
  answer: string;
  strategy: string;
  entities: GraphNode[];
  graph: GraphPayload;
  sources: Source[];
}

export interface AnalyticsOverview {
  nodes: number;
  relationships: number;
  unique_connections: number;
  density: number;
  average_degree: number;
  connected_components: number;
  largest_component: number;
  communities: number;
  community_algorithm: string;
}

export interface CentralityResult {
  rank: number;
  node: GraphNode;
  score: number;
  degree: number;
}

export interface CentralityPayload {
  metric: "degree" | "betweenness";
  node_type: string | null;
  total_considered: number;
  results: CentralityResult[];
}

export interface CommunityResult {
  id: string;
  size: number;
  member_types: Record<string, number>;
  members: GraphNode[];
}

export interface CommunitiesPayload {
  algorithm: string;
  modularity: number;
  count: number;
  total_count: number;
  min_size: number;
  communities: CommunityResult[];
}

export interface SimilarityResult {
  node: GraphNode;
  score: number;
  shared_neighbor_count: number;
  union_neighbor_count: number;
  shared_neighbors: GraphNode[];
}

export interface SimilarityPayload {
  source: GraphNode;
  metric: string;
  compared_type: string;
  results: SimilarityResult[];
}
