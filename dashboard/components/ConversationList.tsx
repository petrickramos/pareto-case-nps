import { ConversationSummary } from "../lib/supabaseClient";

type Props = {
  conversations: ConversationSummary[];
  selectedChatId: string | null;
  onSelect: (chatId: string) => void;
};

function getNpsColor(score: number | null): string {
  if (score === null) return "transparent";
  if (score >= 9) return "#22c55e"; // Promotor
  if (score >= 7) return "#facc15"; // Neutro
  return "#f87171"; // Detrator
}

export default function ConversationList({
  conversations,
  selectedChatId,
  onSelect
}: Props) {
  return (
    <div className="list">
      {conversations.length === 0 && (
        <p className="panel-subtitle">Nenhuma conversa encontrada.</p>
      )}
      {conversations.map((conversation) => {
        const dotColor = getNpsColor(conversation.nps_score);
        return (
          <button
            key={conversation.chat_id}
            className={`list-item ${selectedChatId === conversation.chat_id ? "active" : ""
              }`}
            onClick={() => onSelect(conversation.chat_id)}
          >
            <div className="list-item-header">
              <div className="text-strong chat-id" title={conversation.chat_id}>
                {conversation.chat_id}
              </div>
              {conversation.nps_score !== null && (
                <div
                  className="nps-dot"
                  style={{ backgroundColor: dotColor }}
                  title={`NPS: ${conversation.nps_score}`}
                />
              )}
            </div>
            <p className="list-message">
              {conversation.last_message}
            </p>
            <div className="meta-row">
              <span>{conversation.last_state ?? "sem estado"}</span>
              <span>{new Date(conversation.updated_at).toLocaleString()}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
