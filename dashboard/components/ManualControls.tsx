"use client";

import { useMemo, useState } from "react";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";

type Props = {
  chatId: string | null;
  managerId?: string | null;
};

export default function ManualControls({ chatId, managerId }: Props) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const canSend = useMemo(() => !!chatId && message.trim().length > 0, [chatId, message]);

  const sendManual = async () => {
    if (!chatId || !apiBaseUrl) return;
    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch(`${apiBaseUrl}/telegram/send-manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          message: message.trim(),
          manager_id: managerId || "gestor"
        })
      });

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.detail || "Falha ao enviar mensagem manual.");
      }

      setMessage("");
      if (data?.status === "logged_only") {
        setStatus("Mensagem registrada (chat_id inválido para Telegram).");
      } else {
        setStatus("Mensagem enviada. Bot em modo manual.");
      }
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? `Não foi possível enviar. ${error.message}`
          : "Não foi possível enviar. Verifique o endpoint.";
      setStatus(message);
    } finally {
      setLoading(false);
    }
  };

  const setManualMode = async (enabled: boolean) => {
    if (!chatId || !apiBaseUrl) return;
    setLoading(true);
    setStatus(null);

    try {
      const endpoint = enabled ? "manual/enable" : "manual/disable";
      const response = await fetch(`${apiBaseUrl}/telegram/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, manager_id: managerId || "gestor" })
      });

      if (!response.ok) {
        throw new Error("Falha ao atualizar modo manual.");
      }

      setStatus(enabled ? "Modo manual ativado." : "Modo automático restaurado.");
    } catch (error) {
      setStatus("Não foi possível atualizar o modo manual.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel-body">
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <button
          className="button secondary"
          type="button"
          onClick={() => setManualMode(true)}
          disabled={!chatId || loading}
        >
          Assumir controle
        </button>
        <button
          className="button secondary"
          type="button"
          onClick={() => setManualMode(false)}
          disabled={!chatId || loading}
        >
          Retornar ao automático
        </button>
      </div>

      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="Escreva a resposta manual do gerente..."
      />
      <div style={{ height: 12 }} />
      <button className="button" type="button" onClick={sendManual} disabled={!canSend || loading}>
        {loading ? "Enviando..." : "Enviar mensagem manual"}
      </button>
      {status && <p className="small-note" style={{ marginTop: 10 }}>{status}</p>}
      {!apiBaseUrl && (
        <p className="small-note" style={{ marginTop: 10 }}>
          Configure NEXT_PUBLIC_API_BASE_URL para usar intervenção manual.
        </p>
      )}
    </div>
  );
}
