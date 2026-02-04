# Informações do Projeto - Pareto Case NPS

## Repositório GitHub
**URL**: https://github.com/petrickramos/pareto-case-nps.git  
**Owner**: petrickramos  
**Projeto**: pareto-case-nps

---

## 📋 Enunciado do Case - Pareto/FMA

### Case Agent Dev - Desafio para implementação de Agentes de IA
**Prazo**: 10 dias  
**Instituição**: MBA em Inteligência Artificial - Faculdade Mar Atlântico

### Cenário

A Pareto quer iniciar um piloto de atendimento proativo para medir a satisfação dos clientes, após a conclusão de um serviço ou após determinado tempo como cliente. 

**Processo Atual (Manual)**:
1. Gerentes de Qualidade acessam manualmente o CRM HubSpot
2. Revisam histórico do cliente dos últimos 30 dias
3. Analisam: e-mails, negócios fechados, tickets de churn/downgrade, anotações e produtos contratados
4. Redigem manualmente mensagem personalizada
5. Enviam via canal de mensageria
6. Atribuem nota de 1 a 5 baseada na resposta
7. Registram em planilha

**Problemas Identificados**:
- ⏱️ Processo lento (média de 30 min por cliente)
- ❌ Sujeito a erros de copy/paste
- 📉 Informações se perdem ou ficam inconsistentes
- 🔍 Falta rastreabilidade das mensagens enviadas

### Desafio

Desenhar e prototipar uma solução ponta a ponta que automatize este processo, utilizando IA e automação para:
- Reduzir tempo de processamento
- Garantir consistência
- Melhorar registro das métricas de satisfação

### Entregas Requeridas

#### 1. Mapeamento de Processo (AS-IS & TO-BE)
- Fluxograma do processo atual ("AS-IS")
- Fluxograma do processo otimizado ("TO-BE")

#### 2. Desenho da Solução Técnica
- Componentes da solução (ferramentas, plataformas)
- Detalhamento dos agentes e suas responsabilidades
- Interface de monitoramento para gerentes de qualidade
  - Visualização de conversas
  - Supervisão em tempo real
  - Histórico completo
  - Possibilidade de intervenção manual

#### 3. Fluxo de Automação (AI Workflow)
- Fluxo funcional completo refletindo processo "TO-BE"
- Prints do fluxo com legendas explicativas
- Arquivo de export (n8n .json, Make blueprint, etc.)
- Instruções de execução (variáveis, webhooks, chaves)
- Ao menos 1 transcrição/captura de conversa de teste
- Log de envio/entrega/leitura
- Registro da nota de satisfação
- Vídeo demonstrativo ou demo com tutorial

#### 4. Agentes de IA (Engenharia de Prompt)
- Prompt completo de cada agente
- Justificativa dos parâmetros de configuração
- Links dos agentes públicos
- Simulações de conversa

#### 5. Plano de Projeto
- Principais fases de implementação
- 2-3 atividades-chave por fase
- Entregáveis e estimativa de esforço
- **ROI do Projeto de IA**

### Formato de Entrega
- Documento único em PDF
- Todos os links para arquivos elaborados
- Links públicos (visualização aberta)

---

## Estrutura do Projeto

### Diretório Principal
`/Users/julianamoraesferreira/Documents/Projetos-Dev-Petrick/pareto-case/`

### Componentes
- **langchain/**: Sistema multi-agente NPS com integração Tess AI
- **n8n-exports/**: Workflows do n8n para automação
- **hubspot-mock/**: Mock API do HubSpot (WireMock)

## Integrações

### Tess AI
- **API Base**: https://tess.pareto.io/api
- **Agente Análise**: `petrick-agente-de-analise-de-sentimento-4HjFZi`
- **Agente Mensagens**: `petrick-geracao-de-mensagens-nps-SBdJZp`
- **Endpoint**: OpenAI-compatible (`/agents/{id}/openai/chat/completions`)

### HubSpot Mock
- **Repositório**: https://github.com/fermazim/hubspot_mockapi
- **Clientes**: 101, 102 (ativos), 103 (controle)
- **Auth Token**: `pat-na1-123`

## Tecnologias
- Python 3.8+
- **LangChain** (migrado em 03/02/2026)
- FastAPI
- n8n
- WireMock
- Tess AI API
- Supabase (PostgreSQL)

---

## 🔄 Status do Desenvolvimento

### Migração para LangChain (03/02/2026)
O projeto foi migrado de Python puro para **LangChain** para melhor orquestração dos agentes de IA.

**Mudanças principais**:
- Criado `TessLLM` wrapper customizado para integração Tess + LangChain
- Agentes agora usam `PromptTemplate` e `LLMChain`
- Melhor estruturação de prompts e respostas
- Análise de keywords e sentimentos mais robusta

### Sistema de Auditoria (04/02/2026) - ✅ CONCLUÍDO
Implementado sistema completo de auditoria com Supabase:
- **Schema SQL**: Tabelas `nps_interactions` e `nps_campaigns` criadas e testadas
- **Cliente Python**: `supabase_client.py` implementado com tratamento de erros robusto
- **Integração**: Todos os agentes (`SentimentAnalyzer`, `MessageGenerator`, `ResponseEvaluator`) agora logam automaticamente suas operações
- **Testes**: Script `test_supabase_integration.py` validou o fluxo completo de escrita no banco

**Próximo Passo**: Monitorar ambiente de produção

### Deploy na Vercel (04/02/2026) - ✅ CONCLUÍDO
Configurações para deploy serverless:
- **Environment Variables**:
  - `SUPABASE_URL` / `SUPABASE_KEY`: Credenciais de produção
  - `HUBSPOT_API_URL`: Configurado como `http://localhost:4010` para validação de build (⚠️ Nota: Mock local não acessível externamente em prod)
- **Documentação**: Atualizado `DEPLOY.md` com guia passo-a-passo para Supabase

### Integração Tess AI (Em Andamento)
- ✅ Agentes criados na plataforma Tess
  - `petrick-agente-de-analise-de-sentimento-4HjFZi`
  - `petrick-geracao-de-mensagens-nps-SBdJZp`
- ⏳ Aguardando agentes ficarem públicos
- ✅ Código atualizado com slugs corretos

---

### Ativar ambiente virtual
```bash
cd /Users/julianamoraesferreira/Documents/Projetos-Dev-Petrick/pareto-case/langchain
source venv/bin/activate
```

### Testar integração Tess
```bash
python3 test_public_agents.py  # Testar agentes públicos
python3 test_llm_integration.py  # Teste completo
```

### Rodar API
```bash
python3 api.py
```

## Contatos
- **Desenvolvedor**: Juliana Moraes Ferreira (Petrick)
- **Instituição**: MBA AI Leader - Faculdade Mar Atlântico
- **Projeto**: Case Pareto - Sistema NPS Multi-Agente
