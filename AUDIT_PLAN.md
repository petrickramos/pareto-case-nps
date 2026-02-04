# Plano: Sistema de Auditoria e Deploy

## Status Atual

### ✅ Já Configurado
- **Supabase**: Credenciais configuradas no `.env`
  - URL: `https://dqczihjtuujoqwkdpjgf.supabase.co`
  - Key: Configurada
- **API FastAPI**: Funcionando localmente
- **Integração Tess AI**: Aguardando agentes ficarem públicos
- **HubSpot Mock**: Rodando em `localhost:4010`
- **Sistema de Auditoria**: Implementado `SupabaseClient` e integrado nos agentes
- **Tabelas Supabase**: Criadas e testadas
- **Logging de Interações**: Implementado

### ❌ Pendente
- **Deploy Vercel**: Não verificado se está configurado

## Requisitos do Projeto

Segundo o case da Pareto, é necessário:

1. **Auditoria de todas as interações**:
   - Registro de cada análise de sentimento
   - Registro de cada mensagem gerada
   - Registro de cada resposta NPS recebida
   - Timestamp de todas as operações

2. **Rastreabilidade**:
   - Qual cliente (contact_id)
   - Qual agente processou
   - Entrada e saída de cada agente
   - Sucesso/falha das operações

3. **Análise posterior**:
   - Comparar efetividade das mensagens
   - Identificar padrões de churn
   - Medir performance dos agentes

## Implementação Proposta

### Fase 1: Estrutura do Banco de Dados

#### Tabela: `nps_interactions`
```sql
CREATE TABLE nps_interactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  contact_id VARCHAR(50) NOT NULL,
  interaction_type VARCHAR(50) NOT NULL, -- 'sentiment_analysis', 'message_generation', 'nps_response'
  agent_name VARCHAR(100),
  input_data JSONB,
  output_data JSONB,
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  processing_time_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contact_id ON nps_interactions(contact_id);
CREATE INDEX idx_interaction_type ON nps_interactions(interaction_type);
CREATE INDEX idx_created_at ON nps_interactions(created_at);
```

#### Tabela: `nps_campaigns`
```sql
CREATE TABLE nps_campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  contact_id VARCHAR(50) NOT NULL,
  sentiment_score VARCHAR(20),
  risk_level VARCHAR(20),
  message_sent BOOLEAN DEFAULT false,
  message_content TEXT,
  nps_score INTEGER,
  nps_feedback TEXT,
  campaign_date TIMESTAMP DEFAULT NOW()
);
```

### Fase 2: Cliente Supabase

#### Arquivo: `supabase_client.py`
```python
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)
    
    def log_interaction(self, contact_id, interaction_type, agent_name, 
                       input_data, output_data, success=True, 
                       error_message=None, processing_time_ms=0):
        """Registra uma interação no banco"""
        
    def get_contact_history(self, contact_id):
        """Busca histórico de interações de um contato"""
        
    def get_campaign_stats(self, start_date=None, end_date=None):
        """Retorna estatísticas das campanhas"""
```

### Fase 3: Integração nos Agentes

Modificar cada agente para logar suas operações:

```python
# Em sentiment_analyzer.py
def analyze(self, context):
    start_time = time.time()
    
    try:
        result = self.tess.chat_completion(...)
        processing_time = int((time.time() - start_time) * 1000)
        
        # Logar sucesso
        supabase.log_interaction(
            contact_id=context['cliente']['id'],
            interaction_type='sentiment_analysis',
            agent_name='SentimentAnalyzerAgent',
            input_data=context,
            output_data=result,
            success=True,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        # Logar erro
        supabase.log_interaction(..., success=False, error_message=str(e))
```

### Fase 4: Deploy Vercel

#### Arquivo: `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "TESS_API_KEY": "@tess_api_key",
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_KEY": "@supabase_key",
    "HUBSPOT_API_URL": "@hubspot_api_url",
    "HUBSPOT_API_KEY": "@hubspot_api_key"
  }
}
```

## Próximos Passos

1. **Criar tabelas no Supabase** (via SQL Editor)
2. **Implementar `supabase_client.py`**
3. **Adicionar logging em todos os agentes**
4. **Testar localmente**
5. **Configurar Vercel** (se ainda não estiver)
6. **Deploy e teste em produção**

## Prioridade

1. 🔴 **ALTA**: Sistema de auditoria (requisito do case)
2. 🟡 **MÉDIA**: Deploy Vercel (pode esperar agentes Tess ficarem públicos)
3. 🟢 **BAIXA**: Dashboard de métricas (opcional, mas útil)
