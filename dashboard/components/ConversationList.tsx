import { ConversationSummary } from "../lib/supabaseClient";

type Props = {
  conversations: ConversationSummary[];
  selectedChatId: string | null;
  onSelect: (chatId: string) => void;
};

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
      {conversations.map((conversation) => (
        <button
          key={conversation.chat_id}
          className={`list-item ${
            selectedChatId === conversation.chat_id ? "active" : ""
          }`}
          onClick={() => onSelect(conversation.chat_id)}
        >
          <div className="text-strong">Chat {conversation.chat_id}</div>
          <p style={{ margin: "6px 0", color: "var(--muted)", fontSize: 13 }}>
            {conversation.last_message}
          </p>
          <div className="meta-row">
            <span>{conversation.last_state ?? "sem estado"}</span>
            <span>{new Date(conversation.updated_at).toLocaleString()}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
