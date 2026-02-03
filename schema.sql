-- Schema SQL para Supabase (Postgres)
-- Armazena respostas NPS com feedback qualitativo

CREATE TABLE IF NOT EXISTS nps_respostas (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    username VARCHAR(255),
    nota INTEGER NOT NULL CHECK (nota >= 0 AND nota <= 10),
    feedback_texto TEXT,  -- Feedback qualitativo do cliente
    categoria VARCHAR(20) CHECK (categoria IN ('PROMOTOR', 'NEUTRO', 'DETRATOR')),
    resumo_executivo TEXT,
    resposta_empatica TEXT,  -- Resposta humanizada enviada ao cliente
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_nps_chat_id ON nps_respostas(chat_id);
CREATE INDEX idx_nps_categoria ON nps_respostas(categoria);
CREATE INDEX idx_nps_created_at ON nps_respostas(created_at DESC);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_nps_respostas_updated_at 
    BEFORE UPDATE ON nps_respostas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- View para análise rápida
CREATE OR REPLACE VIEW nps_analytics AS
SELECT 
    categoria,
    COUNT(*) as total,
    ROUND(AVG(nota), 2) as nota_media,
    COUNT(CASE WHEN feedback_texto IS NOT NULL AND feedback_texto != '' THEN 1 END) as com_feedback
FROM nps_respostas
GROUP BY categoria;

-- Comentários para documentação
COMMENT ON TABLE nps_respostas IS 'Armazena todas as respostas de pesquisa NPS dos clientes';
COMMENT ON COLUMN nps_respostas.feedback_texto IS 'Feedback qualitativo opcional fornecido pelo cliente';
COMMENT ON COLUMN nps_respostas.resposta_empatica IS 'Resposta humanizada gerada pelo bot e enviada ao cliente';
COMMENT ON COLUMN nps_respostas.categoria IS 'Classificação NPS: PROMOTOR (9-10), NEUTRO (7-8), DETRATOR (0-6)';
