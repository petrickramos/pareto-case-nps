"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ConversationList from "./ConversationList";
import ConversationDetail from "./ConversationDetail";
import ManualControls from "./ManualControls";
import { supabase, ConversationMessage, ConversationSummary } from "../lib/supabaseClient";

function buildSummary(messages: ConversationMessage[]): ConversationSummary[] {
  const map = new Map<string, ConversationSummary>();

  messages.forEach((message) => {
    const current = map.get(message.chat_id);
    if (!current || new Date(message.created_at) > new Date(current.updated_at)) {
      map.set(message.chat_id, {
        chat_id: message.chat_id,
        last_message: message.message_text,
        last_sender: message.sender,
        last_state: message.conversation_state,
        nps_score: message.nps_score,
        sentiment: message.sentiment,
        updated_at: message.created_at
      });
    }
  });

  return Array.from(map.values()).sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  );
}

export default function Dashboard({ managerId }: { managerId?: string | null }) {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [conversationMessages, setConversationMessages] = useState<ConversationMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const latestMessageRef = useRef<string | null>(null);

  const summaries = useMemo(() => buildSummary(messages), [messages]);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? window.localStorage.getItem("pareto:selectedChatId") : null;
    if (saved) {
      setSelectedChatId(saved);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (selectedChatId) {
      window.localStorage.setItem("pareto:selectedChatId", selectedChatId);
    } else {
      window.localStorage.removeItem("pareto:selectedChatId");
    }
  }, [selectedChatId]);

  useEffect(() => {
    const loadMessages = async () => {
      const { data } = await supabase
        .from("conversation_messages")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(300);

      if (data) {
        setMessages(data as ConversationMessage[]);
        if (data.length > 0) {
          latestMessageRef.current = (data[0] as ConversationMessage).created_at;
        }
      }
      setLoading(false);
    };

    loadMessages();
  }, []);

  useEffect(() => {
    if (!selectedChatId) {
      setConversationMessages([]);
      return;
    }

    const loadConversation = async () => {
      const { data } = await supabase
        .from("conversation_messages")
        .select("*")
        .eq("chat_id", selectedChatId)
        .order("created_at", { ascending: true });

      if (data) {
        setConversationMessages(data as ConversationMessage[]);
      }
    };

    loadConversation();
  }, [selectedChatId]);

  useEffect(() => {
    const channel = supabase
      .channel("conversation_messages")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "conversation_messages" },
        (payload) => {
          const newMessage = payload.new as ConversationMessage;
          setMessages((prev) => [newMessage, ...prev].slice(0, 300));

          if (newMessage.chat_id === selectedChatId) {
            setConversationMessages((prev) => [...prev, newMessage]);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [selectedChatId]);

  useEffect(() => {
    const pollNewMessages = async () => {
      let query = supabase
        .from("conversation_messages")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50);

      if (latestMessageRef.current) {
        query = query.gt("created_at", latestMessageRef.current);
      }

      const { data } = await query;
      if (!data || data.length === 0) {
        return;
      }

      const incoming = data as ConversationMessage[];

      setMessages((prev) => {
        const map = new Map<string, ConversationMessage>();
        prev.forEach((item) => map.set(item.id, item));
        incoming.forEach((item) => map.set(item.id, item));
        const merged = Array.from(map.values()).sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        const next = merged.slice(0, 300);
        latestMessageRef.current = next[0]?.created_at ?? latestMessageRef.current;
        return next;
      });

      if (selectedChatId) {
        const forChat = incoming.filter((item) => item.chat_id === selectedChatId);
        if (forChat.length > 0) {
          setConversationMessages((prev) => {
            const map = new Map<string, ConversationMessage>();
            prev.forEach((item) => map.set(item.id, item));
            forChat.forEach((item) => map.set(item.id, item));
            return Array.from(map.values()).sort(
              (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
          });
        }
      }
    };

    const interval = window.setInterval(pollNewMessages, 5000);
    return () => window.clearInterval(interval);
  }, [selectedChatId]);

  return (
    <div className="app-shell">
      <section className="panel">
        <div className="panel-header">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
            <div>
              <h2 className="panel-title">Conversas</h2>
              <p className="panel-subtitle">
                {loading ? "Carregando conversas..." : `${summaries.length} chats ativos`}
              </p>
            </div>
            <button
              className="button secondary"
              type="button"
              onClick={() => supabase.auth.signOut()}
            >
              Sair
            </button>
          </div>
        </div>
        <div className="panel-body">
          <ConversationList
            conversations={summaries}
            selectedChatId={selectedChatId}
            onSelect={setSelectedChatId}
          />
        </div>
      </section>

      <section className="panel" style={{ display: "flex", flexDirection: "column" }}>
        <div className="panel-header">
          <h2 className="panel-title">Auditoria & Intervenção</h2>
          <p className="panel-subtitle">
            Histórico completo + controle manual do gerente
          </p>
        </div>
        <div className="split" style={{ flex: 1 }}>
          <div className="panel chat-panel" style={{ border: "none", boxShadow: "none" }}>
            <ConversationDetail chatId={selectedChatId} messages={conversationMessages} />
          </div>
          <div className="panel control-panel" style={{ border: "none", boxShadow: "none" }}>
            <ManualControls chatId={selectedChatId} managerId={managerId} />
          </div>
        </div>
      </section>
    </div>
  );
}
