import { useEffect, useRef, useState } from "react";
import { ConversationMessage } from "../lib/supabaseClient";

type Props = {
  chatId: string | null;
  messages: ConversationMessage[];
};

function getSenderLabel(sender: ConversationMessage["sender"]) {
  if (sender === "bot") return "Bot";
  if (sender === "manager") return "Gestor";
  if (sender === "system") return "Sistema";
  return "Cliente";
}

export default function ConversationDetail({ chatId, messages }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [visibleCount, setVisibleCount] = useState(30);

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    setVisibleCount(30);
  }, [chatId]);

  if (!chatId) {
    return (
      <div className="panel-body">
        <p className="panel-subtitle">Selecione uma conversa para visualizar.</p>
      </div>
    );
  }

  const totalMessages = messages.length;
  const visibleMessages = messages.slice(Math.max(0, totalMessages - visibleCount));
  const remaining = totalMessages - visibleMessages.length;

  return (
    <div className="panel-body conversation-detail">
      <div style={{ marginBottom: 16 }}>
        <div className="text-strong chat-id" title={chatId}>
          Chat {chatId}
        </div>
        <div className="panel-subtitle">Histórico completo da conversa</div>
      </div>
      {remaining > 0 && (
        <div style={{ marginBottom: 12 }}>
          <button
            className="button secondary small"
            type="button"
            onClick={() => setVisibleCount((current) => Math.min(current + 20, totalMessages))}
          >
            Ver mais ({remaining})
          </button>
        </div>
      )}
      <div className="conversation-scroll" ref={scrollRef}>
        {totalMessages === 0 && (
          <p className="panel-subtitle">Nenhuma mensagem encontrada.</p>
        )}
        {visibleMessages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="meta-row" style={{ marginBottom: 6 }}>
              <span className="text-strong">{getSenderLabel(message.sender)}</span>
              <span>{new Date(message.created_at).toLocaleString()}</span>
            </div>
            <div>{message.message_text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
