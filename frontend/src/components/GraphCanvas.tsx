import cytoscape, { Core, ElementDefinition, NodeSingular } from "cytoscape";
import { Focus, Lock, Minus, Plus } from "lucide-react";
import { memo, useEffect, useMemo, useRef } from "react";
import type { GraphEdge, GraphNode } from "../types";

const NODE_COLORS: Record<string, string> = {
  Character: "#f0283c",
  Universe: "#31c6cf",
  Event: "#f3a21b",
  Team: "#a45ee5",
  Work: "#84a3b8",
  Power: "#6ecb8f",
  Concept: "#c9d1da",
};

const NODE_SHAPES: Record<string, cytoscape.Css.NodeShape> = {
  Character: "ellipse",
  Universe: "rectangle",
  Event: "diamond",
  Team: "hexagon",
  Work: "round-rectangle",
  Power: "round-rectangle",
  Concept: "round-rectangle",
};

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  focusId: string | null;
  selectedId: string | null;
  onSelect: (node: GraphNode) => void;
}

function GraphCanvasComponent({ nodes, edges, focusId, selectedId, onSelect }: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const nodeMap = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes]);

  useEffect(() => {
    if (!containerRef.current) return;
    const elements: ElementDefinition[] = [
      ...nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          nodeType: node.type,
          color: NODE_COLORS[node.type] ?? "#c9d1da",
          shape: NODE_SHAPES[node.type] ?? "ellipse",
        },
        classes: node.id === focusId ? "focus-node" : "",
      })),
      ...edges.map((edge) => ({
        data: { id: edge.id, source: edge.source, target: edge.target, label: edge.type },
      })),
    ];
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      minZoom: 0.35,
      maxZoom: 2.5,
      style: [
        {
          selector: "node",
          style: {
            width: 72,
            height: 72,
            shape: "data(shape)" as cytoscape.Css.NodeShape,
            "background-color": "#09121d",
            "border-width": 2,
            "border-color": "data(color)",
            label: "data(label)",
            color: "#f5f1e8",
            "font-family": "Inter, sans-serif",
            "font-size": 11,
            "font-weight": 600,
            "text-wrap": "wrap",
            "text-max-width": "74px",
            "text-valign": "center",
            "text-halign": "center",
            "overlay-opacity": 0,
            "transition-property": "border-width, width, height, background-color",
            "transition-duration": 160,
          },
        },
        {
          selector: "node[nodeType = 'Universe'], node[nodeType = 'Work']",
          style: { width: 92, height: 56 },
        },
        {
          selector: "node[nodeType = 'Power'], node[nodeType = 'Concept']",
          style: { width: 104, height: 42, "font-size": 10 },
        },
        {
          selector: "node.focus-node",
          style: { width: 94, height: 94, "border-width": 4, "background-color": "#111b27", "font-size": 13 },
        },
        {
          selector: "node:selected",
          style: { "border-width": 5, "background-color": "#162230" },
        },
        {
          selector: "edge",
          style: {
            width: 1.4,
            "line-color": "#526171",
            "target-arrow-color": "#526171",
            "target-arrow-shape": "triangle",
            "arrow-scale": 0.75,
            "curve-style": "bezier",
            label: "data(label)",
            color: "#9ba7b5",
            "font-family": "Inter, sans-serif",
            "font-size": 8,
            "text-rotation": "autorotate",
            "text-margin-y": -7,
            "text-background-color": "#07101a",
            "text-background-opacity": 0.88,
            "text-background-padding": "2px",
            "overlay-opacity": 0,
          },
        },
        { selector: "edge:selected", style: { width: 2.5, "line-color": "#f0283c", "target-arrow-color": "#f0283c" } },
      ],
      layout: {
        name: "concentric",
        fit: true,
        padding: 62,
        minNodeSpacing: 64,
        concentric: (node: NodeSingular) => node.id() === focusId ? 10 : Math.max(1, node.degree()),
        levelWidth: () => 2,
        animate: false,
      },
    });
    cy.on("tap", "node", (event) => {
      const node = nodeMap.get(event.target.id());
      if (node) onSelect(node);
    });
    if (selectedId) cy.getElementById(selectedId).select();
    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [edges, focusId, nodeMap, nodes, onSelect, selectedId]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !selectedId) return;
    cy.nodes().unselect();
    cy.getElementById(selectedId).select();
  }, [selectedId]);

  function zoom(factor: number) {
    const cy = cyRef.current;
    if (!cy) return;
    cy.zoom({ level: cy.zoom() * factor, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  }

  return (
    <div className="graph-frame">
      <div ref={containerRef} className="graph-canvas" aria-label="Interactive knowledge graph" />
      <div className="graph-tools" aria-label="Graph controls">
        <button type="button" onClick={() => cyRef.current?.fit(undefined, 48)} aria-label="Fit graph"><Focus size={17} /></button>
        <button type="button" onClick={() => zoom(1.18)} aria-label="Zoom in"><Plus size={17} /></button>
        <button type="button" onClick={() => zoom(0.84)} aria-label="Zoom out"><Minus size={17} /></button>
        <button type="button" onClick={() => cyRef.current?.autolock(!cyRef.current.autolock())} aria-label="Lock nodes"><Lock size={16} /></button>
      </div>
      <div className="canvas-key">
        <span><i className="type-character" />Character</span>
        <span><i className="type-universe" />Universe</span>
        <span><i className="type-event" />Event</span>
        <span><i className="type-team" />Team</span>
      </div>
    </div>
  );
}

export const GraphCanvas = memo(GraphCanvasComponent);
