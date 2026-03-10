"use client";

import { FormEvent, useState } from "react";

import { CopilotQueryResponse, queryCopilot } from "../../lib/api";

export default function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<CopilotQueryResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await queryCopilot({
        question: question.trim(),
        locale: "pt-BR",
      });
      setResult(response);
    } catch (submissionError) {
      const message =
        submissionError instanceof Error
          ? submissionError.message
          : "Nao foi possivel consultar o copilot.";
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="stack">
      <header>
        <p className="eyebrow">Copilot</p>
        <h2>Consulta grounded sobre o hub publico</h2>
        <p className="muted">
          O copilot responde com base nas versoes publicadas do hub e devolve
          citacoes rastreaveis.
        </p>
      </header>

      <form className="card stack" onSubmit={handleSubmit}>
        <label className="field">
          <span className="eyebrow">Pergunta</span>
          <textarea
            className="textarea"
            placeholder="Ex.: Quais mudancas recentes apareceram no PLD horario do Sudeste?"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={5}
          />
        </label>
        <div className="row">
          <button className="button" type="submit" disabled={loading}>
            {loading ? "Consultando..." : "Perguntar"}
          </button>
          {error ? <span className="critical">{error}</span> : null}
        </div>
      </form>

      {result ? (
        <article className="card stack">
          <div>
            <p className="eyebrow">Resposta</p>
            <p>{result.answer}</p>
          </div>

          <div>
            <p className="eyebrow">Citacoes</p>
            <ul className="list">
              {result.citations.map((citation) => (
                <li key={`${citation.version_id}-${citation.entity_id ?? "scope"}`}>
                  {citation.source_code} / {citation.dataset_id} / {citation.version_id}
                  {citation.entity_id ? ` / ${citation.entity_id}` : ""}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="eyebrow">Proximas perguntas</p>
            <ul className="list">
              {result.follow_up_questions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </article>
      ) : null}
    </section>
  );
}
