"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { supabase, ConversationMessage } from "../lib/supabaseClient";

type ScoreSnapshot = Pick<ConversationMessage, "chat_id" | "nps_score" | "sentiment" | "created_at">;

type ScoreCategory = "PROMOTOR" | "NEUTRO" | "DETRATOR";

type MetricsSummary = {
  total: number;
  avgScore: number;
  npsScore: number;
  promotores: number;
  neutros: number;
  detratores: number;
  positivos: number;
  neutrosSent: number;
  negativos: number;
};

const SCORE_COLORS: Record<ScoreCategory, string> = {
  PROMOTOR: "#22c55e",
  NEUTRO: "#facc15",
  DETRATOR: "#f87171"
};

const SENTIMENT_COLORS = {
  POSITIVO: "#22c55e",
  NEUTRO: "#facc15",
  NEGATIVO: "#f87171"
};

function classifyScore(score: number): ScoreCategory {
  if (score >= 9) {
    return "PROMOTOR";
  }
  if (score >= 7) {
    return "NEUTRO";
  }
  return "DETRATOR";
}

function normalizeSentiment(sentiment: string | null): "POSITIVO" | "NEUTRO" | "NEGATIVO" {
  if (!sentiment) {
    return "NEUTRO";
  }
  const normalized = sentiment.toUpperCase();
  if (normalized.includes("POS")) {
    return "POSITIVO";
  }
  if (normalized.includes("NEG")) {
    return "NEGATIVO";
  }
  return "NEUTRO";
}

function MetricBar({
  label,
  value,
  total,
  color
}: {
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const percent = total > 0 ? Math.round((value / total) * 100) : 0;

  return (
    <div className="metric-bar">
      <div className="metric-bar-header">
        <span>{label}</span>
        <span>
          {value} ({percent}%)
        </span>
      </div>
      <div className="metric-bar-track">
        <div className="metric-bar-fill" style={{ width: `${percent}%`, background: color }} />
      </div>
    </div>
  );
}

export default function MetricsDashboard() {
  const [snapshots, setSnapshots] = useState<ScoreSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("-");
  const [error, setError] = useState<string | null>(null);

  const loadMetrics = useCallback(async () => {
    setError(null);
    const { data, error: queryError } = await supabase
      .from("conversation_messages")
      .select("chat_id, nps_score, sentiment, created_at")
      .not("nps_score", "is", null)
      .order("created_at", { ascending: false })
      .limit(1000);

    if (queryError) {
      setError(queryError.message);
      setLoading(false);
      return;
    }

    if (!data) {
      setSnapshots([]);
      setLoading(false);
      return;
    }

    const seen = new Set<string>();
    const latest: ScoreSnapshot[] = [];
    (data as ScoreSnapshot[]).forEach((item) => {
      if (!seen.has(item.chat_id)) {
        seen.add(item.chat_id);
        latest.push(item);
      }
    });

    setSnapshots(latest);
    setLastUpdated(new Date().toLocaleString("pt-BR"));
    setLoading(false);
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  useEffect(() => {
    const interval = window.setInterval(loadMetrics, 10000);
    return () => window.clearInterval(interval);
  }, [loadMetrics]);

  const summary = useMemo<MetricsSummary>(() => {
    let total = 0;
    let sum = 0;
    let promotores = 0;
    let neutros = 0;
    let detratores = 0;
    let positivos = 0;
    let neutrosSent = 0;
    let negativos = 0;

    snapshots.forEach((item) => {
      if (item.nps_score === null || item.nps_score === undefined) {
        return;
      }
      total += 1;
      sum += item.nps_score;
      const category = classifyScore(item.nps_score);
      if (category === "PROMOTOR") promotores += 1;
      if (category === "NEUTRO") neutros += 1;
      if (category === "DETRATOR") detratores += 1;

      const sentiment = normalizeSentiment(item.sentiment);
      if (sentiment === "POSITIVO") positivos += 1;
      if (sentiment === "NEUTRO") neutrosSent += 1;
      if (sentiment === "NEGATIVO") negativos += 1;
    });

    const avgScore = total > 0 ? Number((sum / total).toFixed(1)) : 0;
    const npsScore = total > 0 ? Math.round(((promotores - detratores) / total) * 100) : 0;

    return {
      total,
      avgScore,
      npsScore,
      promotores,
      neutros,
      detratores,
      positivos,
      neutrosSent,
      negativos
    };
  }, [snapshots]);

  return (
    <div className="metrics-shell">
      <header className="metrics-header">
        <div>
          <h1 className="panel-title">Metricas NPS</h1>
          <p className="panel-subtitle">
            Atualizacao automatica a cada 10s · Ultima: {lastUpdated}
          </p>
        </div>
        <div className="metrics-actions">
          <a className="button secondary" href="/">
            Voltar
          </a>
          <button className="button secondary" type="button" onClick={loadMetrics}>
            Atualizar agora
          </button>
        </div>
      </header>

      <section className="metrics-grid">
        <div className="panel metric-card">
          <p className="metric-label">Total de respostas</p>
          <p className="metric-value">{summary.total}</p>
          <p className="metric-helper">Chats unicos com nota</p>
        </div>
        <div className="panel metric-card">
          <p className="metric-label">Nota media</p>
          <p className="metric-value">{summary.avgScore}</p>
          <p className="metric-helper">Escala 0-10</p>
        </div>
        <div className="panel metric-card">
          <p className="metric-label">NPS</p>
          <p className="metric-value">{summary.npsScore}</p>
          <p className="metric-helper">Promotores - Detratores</p>
        </div>
        <div className="panel metric-card">
          <p className="metric-label">Promotores</p>
          <p className="metric-value">{summary.promotores}</p>
          <p className="metric-helper">Notas 9-10</p>
        </div>
      </section>

      <section className="metrics-charts">
        <div className="panel metric-chart">
          <div className="panel-header">
            <h2 className="panel-title">Distribuicao NPS</h2>
            <p className="panel-subtitle">Promotores, neutros e detratores</p>
          </div>
          <div className="panel-body">
            {loading ? (
              <p className="metric-empty">Carregando dados...</p>
            ) : summary.total === 0 ? (
              <p className="metric-empty">Sem respostas com nota ainda.</p>
            ) : (
              <>
                <MetricBar
                  label="Promotores"
                  value={summary.promotores}
                  total={summary.total}
                  color={SCORE_COLORS.PROMOTOR}
                />
                <MetricBar
                  label="Neutros"
                  value={summary.neutros}
                  total={summary.total}
                  color={SCORE_COLORS.NEUTRO}
                />
                <MetricBar
                  label="Detratores"
                  value={summary.detratores}
                  total={summary.total}
                  color={SCORE_COLORS.DETRATOR}
                />
              </>
            )}
          </div>
        </div>

        <div className="panel metric-chart">
          <div className="panel-header">
            <h2 className="panel-title">Sentimentos</h2>
            <p className="panel-subtitle">Baseado no analise de feedback</p>
          </div>
          <div className="panel-body">
            {loading ? (
              <p className="metric-empty">Carregando dados...</p>
            ) : summary.total === 0 ? (
              <p className="metric-empty">Sem sentimento registrado.</p>
            ) : (
              <>
                <MetricBar
                  label="Positivo"
                  value={summary.positivos}
                  total={summary.total}
                  color={SENTIMENT_COLORS.POSITIVO}
                />
                <MetricBar
                  label="Neutro"
                  value={summary.neutrosSent}
                  total={summary.total}
                  color={SENTIMENT_COLORS.NEUTRO}
                />
                <MetricBar
                  label="Negativo"
                  value={summary.negativos}
                  total={summary.total}
                  color={SENTIMENT_COLORS.NEGATIVO}
                />
              </>
            )}
          </div>
        </div>
      </section>

      {error && (
        <div className="panel metric-card">
          <p className="metric-label">Erro ao carregar dados</p>
          <p className="metric-helper">{error}</p>
        </div>
      )}
    </div>
  );
}
