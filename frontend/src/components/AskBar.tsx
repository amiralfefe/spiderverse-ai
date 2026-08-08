import { Network, Send, X } from "lucide-react";
import { FormEvent, useState } from "react";
import { api } from "../api";
import type { AskResponse, GraphPayload } from "../types";

interface AskBarProps {
  onGraphResult: (graph: GraphPayload) => void;
}

export function AskBar({ onGraphResult }: AskBarProps) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (question.trim().length < 2 || loading) return;
    setLoading(true);
    setError("");
    try {
      const next = await api.ask(question.trim());
      setResult(next);
      if (next.graph.nodes.length > 0) onGraphResult(next.graph);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The graph query failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ask-dock">
      {result || error ? (
        <div className="ask-answer" role="status">
          <Network size={17} />
          <div><strong>{result ? "Graph-grounded answer" : "Query error"}</strong><p>{result?.answer ?? error}</p></div>
          <button type="button" onClick={() => { setResult(null); setError(""); }} aria-label="Close answer"><X size={16} /></button>
        </div>
      ) : null}
      <form onSubmit={submit}>
        <Network size={19} aria-hidden="true" />
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask anything about the Spider-Verse…"
          aria-label="Ask SpiderVerse AI"
        />
        <button type="submit" disabled={loading || question.trim().length < 2}>
          <Send size={16} /> {loading ? "Retrieving" : "Ask"}
        </button>
      </form>
      <p>Try: “Who mentored Miles Morales?” <i /> “Show Gwen Stacy’s allies” <i /> “Path between Miles Morales and Daredevil”</p>
    </div>
  );
}
