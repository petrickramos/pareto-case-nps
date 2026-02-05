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
  if (!chatId) {
    return (
      <div className="panel-body">
        <p className="panel-subtitle">Selecione uma conversa para visualizar.</p>
      </div>
    );
  }

  return (
    <div className="panel-body">
      <div style={{ marginBottom: 16 }}>
        <div className="text-strong">Chat {chatId}</div>
        <div className="panel-subtitle">Histórico completo da conversa</div>
      </div>
      {messages.length === 0 && (
        <p className="panel-subtitle">Nenhuma mensagem encontrada.</p>
      )}
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.sender}`}>
          <div className="meta-row" style={{ marginBottom: 6 }}>
            <span className="text-strong">{getSenderLabel(message.sender)}</span>
            <span>{new Date(message.created_at).toLocaleString()}</span>
          </div>
          <div>{message.message_text}</div>
        </div>
      ))}
    </div>
  );
}
