"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { supabase, ConversationMessage } from "../lib/supabaseClient";

type ScoreSnapshot = Pick<ConversationMessage, "chat_id" | "nps_score" | "created_at">;

type ScoreCategory = "PROMOTOR" | "NEUTRO" | "DETRATOR";

type MetricsSummary = {
  total: number;
  avgScore: number;
  npsScore: number;
  promotores: number;
  neutros: number;
  detratores: number;
};

const SCORE_COLORS: Record<ScoreCategory, string> = {
  PROMOTOR: "#22c55e",
  NEUTRO: "#facc15",
  DETRATOR: "#f87171"
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

function buildPieGradient(segments: { value: number; color: string }[], total: number) {
  if (total <= 0) {
    return "conic-gradient(from -90deg, rgba(255,255,255,0.08) 0 100%)";
  }
  let cursor = 0;
  const stops: string[] = [];
  segments.forEach((segment) => {
    const percent = (segment.value / total) * 100;
    if (percent <= 0) return;
    const start = cursor;
    const end = cursor + percent;
    stops.push(`${segment.color} ${start}% ${end}%`);
    cursor = end;
  });
  if (stops.length === 0) {
    return "conic-gradient(from -90deg, rgba(255,255,255,0.08) 0 100%)";
  }
  return `conic-gradient(from -90deg, ${stops.join(", ")})`;
}

function polarToCartesian(cx: number, cy: number, r: number, angle: number) {
  const rad = (Math.PI / 180) * angle;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad)
  };
}

function describeRingSegment(
  cx: number,
  cy: number,
  rOuter: number,
  rInner: number,
  startAngle: number,
  endAngle: number
) {
  const startOuter = polarToCartesian(cx, cy, rOuter, startAngle);
  const endOuter = polarToCartesian(cx, cy, rOuter, endAngle);
  const startInner = polarToCartesian(cx, cy, rInner, endAngle);
  const endInner = polarToCartesian(cx, cy, rInner, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;

  return [
    `M ${startOuter.x} ${startOuter.y}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${endOuter.x} ${endOuter.y}`,
    `L ${startInner.x} ${startInner.y}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 0 ${endInner.x} ${endInner.y}`,
    "Z"
  ].join(" ");
}

function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(cx, cy, r, startAngle);
  const end = polarToCartesian(cx, cy, r, endAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;

  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

export default function MetricsDashboard() {
  const [snapshots, setSnapshots] = useState<ScoreSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("-");
  const [error, setError] = useState<string | null>(null);
  const [distributionView, setDistributionView] = useState<"gauge" | "pie">("gauge");

  const loadMetrics = useCallback(async () => {
    setError(null);
    const { data, error: queryError } = await supabase
      .from("conversation_messages")
      .select("chat_id, nps_score, created_at")
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
    });

    const avgScore = total > 0 ? Number((sum / total).toFixed(1)) : 0;
    const npsScore = total > 0 ? Math.round(((promotores - detratores) / total) * 100) : 0;

    return {
      total,
      avgScore,
      npsScore,
      promotores,
      neutros,
      detratores
    };
  }, [snapshots]);

  const distributionSegments = useMemo(
    () => [
      { label: "Promotores", value: summary.promotores, color: SCORE_COLORS.PROMOTOR },
      { label: "Neutros", value: summary.neutros, color: SCORE_COLORS.NEUTRO },
      { label: "Detratores", value: summary.detratores, color: SCORE_COLORS.DETRATOR }
    ],
    [summary]
  );

  const pieGradient = useMemo(
    () => buildPieGradient(distributionSegments, summary.total),
    [distributionSegments, summary.total]
  );

  const clampedNps = Math.max(-100, Math.min(100, summary.npsScore));
  const needleAngle = 180 + ((clampedNps + 100) / 200) * 180;

  const gaugeSegments = useMemo(
    () => [
      { color: "#e53935" },
      { color: "#f57c00" },
      { color: "#fdd835" },
      { color: "#cddc39" },
      { color: "#43a047" },
      { color: "#26c6da" }
    ],
    []
  );

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

      <section className="metrics-charts single">
        <div className="panel metric-chart">
          <div className="panel-header">
            <div className="metric-chart-header">
              <div>
                <h2 className="panel-title">Distribuicao NPS</h2>
                <p className="panel-subtitle">Promotores, neutros e detratores</p>
              </div>
              <div className="toggle-group" role="group" aria-label="Visualizacao do grafico">
                <button
                  className={`toggle-button ${distributionView === "gauge" ? "active" : ""}`}
                  type="button"
                  onClick={() => setDistributionView("gauge")}
                  aria-pressed={distributionView === "gauge"}
                >
                  Velocimetro
                </button>
                <button
                  className={`toggle-button ${distributionView === "pie" ? "active" : ""}`}
                  type="button"
                  onClick={() => setDistributionView("pie")}
                  aria-pressed={distributionView === "pie"}
                >
                  Pizza
                </button>
              </div>
            </div>
          </div>
          <div className="panel-body">
            {loading ? (
              <p className="metric-empty">Carregando dados...</p>
            ) : summary.total === 0 ? (
              <p className="metric-empty">Sem respostas com nota ainda.</p>
            ) : distributionView === "gauge" ? (
              <div className="gauge-layout">
                <div className="gauge-visual">
                  <svg className="gauge-svg" viewBox="0 0 200 120" role="img" aria-label="NPS gauge">
                    {gaugeSegments.map((segment, index) => {
                      const start = 180 + index * 30;
                      const end = start + 30;
                      return (
                        <path
                          key={segment.color}
                          d={describeRingSegment(100, 100, 90, 60, start, end)}
                          fill={segment.color}
                        />
                      );
                    })}
                    <path
                      d={describeArc(100, 100, 90, 180, 360)}
                      className="gauge-outline"
                    />
                    <circle cx="100" cy="100" r="52" className="gauge-inner" />
                    <line
                      x1="100"
                      y1="100"
                      x2={polarToCartesian(100, 100, 68, needleAngle).x}
                      y2={polarToCartesian(100, 100, 68, needleAngle).y}
                      className="gauge-needle-line"
                    />
                    <circle cx="100" cy="100" r="8" className="gauge-pivot" />
                  </svg>
                </div>
                <div className="gauge-meta">
                  <div className="gauge-score">{summary.npsScore}</div>
                  <div className="gauge-caption">NPS geral · escala -100 a 100</div>
                  <div className="pie-legend">
                    {distributionSegments.map((segment) => {
                      const percent =
                        summary.total > 0 ? Math.round((segment.value / summary.total) * 100) : 0;
                      return (
                        <div key={segment.label} className="legend-row">
                          <span className="legend-dot" style={{ background: segment.color }} />
                          <span className="legend-label">{segment.label}</span>
                          <span className="legend-value">
                            {segment.value} ({percent}%)
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="pie-layout">
                <div className="pie-chart" style={{ background: pieGradient }}>
                  <div className="pie-center">
                    <div className="pie-total">{summary.total}</div>
                    <div className="pie-label">respostas</div>
                  </div>
                </div>
                <div className="pie-legend">
                  {distributionSegments.map((segment) => {
                    const percent =
                      summary.total > 0 ? Math.round((segment.value / summary.total) * 100) : 0;
                    return (
                      <div key={segment.label} className="legend-row">
                        <span className="legend-dot" style={{ background: segment.color }} />
                        <span className="legend-label">{segment.label}</span>
                        <span className="legend-value">
                          {segment.value} ({percent}%)
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
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
