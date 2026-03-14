"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { type CopilotQueryRequest, type CopilotQueryResponse, queryCopilot } from "../../lib/api";

export function CopilotClient({
  datasetId,
  entityId,
}: {
  datasetId?: string;
  entityId?: string;
}) {
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
      const payload: CopilotQueryRequest = {
        question: question.trim(),
        locale: "pt-BR",
      };

      if (datasetId) {
        payload.dataset_ids = [datasetId];
      }

      if (entityId) {
        payload.entity_ids = [entityId];
      }

      const response = await queryCopilot(payload);
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
    <div className="stack">
      <section className="panel">
        <div className="pageHeader">
          <p className="pageKicker">Grounded Q&A</p>
          <h2 className="workspaceTitle">Consulta grounded sobre o hub publico</h2>
          <p className="pageSubtitle">
            O copilot responde com base nas versoes publicadas do hub e devolve citacoes
            rastreaveis.
          </p>
        </div>

        {datasetId || entityId ? (
          <div className="summaryGrid">
            {datasetId ? (
              <article className="summaryCard">
                <span className="summaryLabel">Dataset em contexto</span>
                <strong>{datasetId}</strong>
              </article>
            ) : null}
            {entityId ? (
              <article className="summaryCard">
                <span className="summaryLabel">Entidade em contexto</span>
                <strong>{entityId}</strong>
              </article>
            ) : null}
          </div>
        ) : null}

        <form className="stack" onSubmit={handleSubmit}>
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
      </section>

      {result ? (
        <article className="panel">
          <div>
            <p className="eyebrow">Resposta</p>
            <p>{result.answer}</p>
          </div>

          <div>
            <p className="eyebrow">Citacoes</p>
            <ul className="list">
              {result.citations.map((citation) => (
                <li key={`${citation.version_id}-${citation.entity_id ?? "scope"}`}>
                  <Link href={`/datasets/${citation.dataset_id}`}>{citation.dataset_name}</Link>
                  {" / "}
                  {citation.version_label}
                  {citation.entity_id ? (
                    <>
                      {" / "}
                      <Link href={`/entities/${citation.entity_id}`}>
                        {citation.entity_name || citation.entity_id}
                      </Link>
                    </>
                  ) : null}
                  {" / "}
                  {citation.source_code}
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
    </div>
  );
}
