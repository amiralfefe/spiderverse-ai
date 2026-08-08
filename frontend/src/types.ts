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
