-- ============================================
-- SCHEMA DE AUDITORIA - PARETO CASE NPS
-- ============================================
-- Execute este script no SQL Editor do Supabase
-- URL: https://dqczihjtuujoqwkdpjgf.supabase.co

-- Tabela principal de interações
CREATE TABLE IF NOT EXISTS nps_interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id VARCHAR(50) NOT NULL,
  interaction_type VARCHAR(50) NOT NULL,
  agent_name VARCHAR(100),
  input_data JSONB,
  output_data JSONB,
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  processing_time_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_nps_interactions_contact_id ON nps_interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_nps_interactions_type ON nps_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_nps_interactions_created_at ON nps_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_nps_interactions_success ON nps_interactions(success);

-- Tabela de campanhas NPS
CREATE TABLE IF NOT EXISTS nps_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id VARCHAR(50) NOT NULL UNIQUE,
  contact_name VARCHAR(200),
  contact_email VARCHAR(200),
  sentiment_score VARCHAR(20),
  risk_level VARCHAR(20),
  message_sent BOOLEAN DEFAULT false,
  message_subject TEXT,
  message_content TEXT,
  message_tone VARCHAR(50),
  nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),
  nps_feedback TEXT,
  nps_category VARCHAR(20),
  campaign_date TIMESTAMP DEFAULT NOW(),
  response_date TIMESTAMP
);

-- Índices para campanhas
CREATE INDEX IF NOT EXISTS idx_nps_campaigns_contact_id ON nps_campaigns(contact_id);
CREATE INDEX IF NOT EXISTS idx_nps_campaigns_sentiment ON nps_campaigns(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_nps_campaigns_risk ON nps_campaigns(risk_level);
CREATE INDEX IF NOT EXISTS idx_nps_campaigns_score ON nps_campaigns(nps_score);
CREATE INDEX IF NOT EXISTS idx_nps_campaigns_category ON nps_campaigns(nps_category);

-- View para dashboard de métricas
CREATE OR REPLACE VIEW nps_metrics AS
SELECT 
  COUNT(*) as total_campaigns,
  COUNT(CASE WHEN nps_score IS NOT NULL THEN 1 END) as total_responses,
  ROUND(AVG(nps_score), 2) as avg_nps_score,
  COUNT(CASE WHEN nps_category = 'PROMOTOR' THEN 1 END) as promotores,
  COUNT(CASE WHEN nps_category = 'NEUTRO' THEN 1 END) as neutros,
  COUNT(CASE WHEN nps_category = 'DETRATOR' THEN 1 END) as detratores,
  COUNT(CASE WHEN risk_level = 'ALTO' THEN 1 END) as alto_risco,
  COUNT(CASE WHEN risk_level = 'MEDIO' THEN 1 END) as medio_risco,
  COUNT(CASE WHEN risk_level = 'BAIXO' THEN 1 END) as baixo_risco
FROM nps_campaigns;

-- Comentários para documentação
COMMENT ON TABLE nps_interactions IS 'Registro de todas as interações dos agentes com clientes';
COMMENT ON TABLE nps_campaigns IS 'Registro consolidado de campanhas NPS por cliente';
COMMENT ON VIEW nps_metrics IS 'Métricas agregadas para dashboard de NPS';

-- Habilitar Row Level Security (RLS)
ALTER TABLE nps_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE nps_campaigns ENABLE ROW LEVEL SECURITY;

-- Política de acesso
CREATE POLICY "Enable all access for service role" ON nps_interactions
  FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON nps_campaigns
  FOR ALL USING (true);
