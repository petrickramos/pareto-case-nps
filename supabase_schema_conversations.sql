-- Tabela para histórico completo de conversas
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id TEXT NOT NULL,
    message_text TEXT NOT NULL,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'bot', 'manager', 'system')),
    conversation_state TEXT,
    nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),
    sentiment TEXT,
    manual_mode BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_conversation_chat_id ON conversation_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created_at ON conversation_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_sender ON conversation_messages(sender);
CREATE INDEX IF NOT EXISTS idx_conversation_state ON conversation_messages(conversation_state);

-- Comentários
COMMENT ON TABLE conversation_messages IS 'Histórico completo de mensagens das conversas NPS via Telegram';
COMMENT ON COLUMN conversation_messages.sender IS 'Quem enviou: user (cliente), bot (automático), manager (gerente manual), system (transições)';
COMMENT ON COLUMN conversation_messages.conversation_state IS 'Estado da conversa: idle, waiting_score, waiting_feedback, completed, manual_mode';
COMMENT ON COLUMN conversation_messages.manual_mode IS 'Se true, bot não responde automaticamente (gerente assumiu controle)';
