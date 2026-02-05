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

---

## 📂 Catálogo Completo de Arquivos (`/langchain`)

### 🎯 Arquivos Principais (Core)

#### `api.py` (12.5 KB)
**Descrição:** Aplicação FastAPI principal com webhook do Telegram  
**Responsabilidades:**
- Endpoint `/telegram/webhook` - Recebe mensagens do Telegram
- Endpoint `/health` - Health check
- Integração com `ConversationManager`
- Envio de respostas via Telegram Bot API

**Dependências:** `conversation_manager.py`, `telegram_client.py`

---

#### `conversation_manager.py` (20.4 KB) ⭐ CRÍTICO
**Descrição:** Orquestrador principal do sistema, gerencia máquina de estados  
**Responsabilidades:**
- Gerenciamento de sessões de conversa
- Máquina de estados (IDLE → WAITING_CONFIRMATION → WAITING_SCORE → COMPLETED)
- Orquestração de agentes (Sentiment, Empathetic Response)
- Extração e validação de score NPS
- Identificação de clientes (integração com `ClienteService`)
- Persistência no Supabase

**Estados:**
- `IDLE`: Aguardando /start
- `WAITING_CONFIRMATION`: Aguardando confirmação/dúvida
- `WAITING_SCORE`: Aguardando nota NPS
- `WAITING_FEEDBACK`: Aguardando justificativa textual (opcional)
- `COMPLETED`: Avaliação registrada

**Dependências:** Todos os agentes, `tess_client.py`, `supabase_client.py`

---

#### `tess_client.py` (5.7 KB) ⭐ CRÍTICO
**Descrição:** Cliente HTTP para API Tess AI  
**Responsabilidades:**
- Comunicação com endpoint OpenAI-compatible da Tess
- Geração de respostas via LLM
- Tratamento de erros e fallback
- Logging detalhado para debug

**Payload Crítico:**
```python
{
    "messages": [...],
    "tools": "no-tools",
    "temperature": 0 ou 1,  # Inteiro!
    "max_tokens": 300,
    "stream": False
}
```

**Commits Recentes:** `f052008` (correção erro 422)

---

#### `supabase_client.py` (4.8 KB)
**Descrição:** Cliente Supabase para persistência  
**Responsabilidades:**
- Conexão com Supabase
- Operações CRUD em tabelas `nps_responses` e `conversation_messages`
- Tratamento de erros de conexão

**Tabelas:**
- `nps_responses`: Avaliações NPS
- `conversation_messages`: Histórico de mensagens

---

### 🤖 Agentes (`/agents`)

#### `sentiment_analyzer.py` (10.8 KB)
**Descrição:** Agente de análise de sentimento  
**Responsabilidades:**
- Analisa score NPS + feedback textual
- Retorna JSON estruturado:
  - `sentimento`: POSITIVO/NEUTRO/NEGATIVO
  - `categoria_nps`: PROMOTOR/NEUTRO/DETRATOR
  - `risco_churn`: BAIXO/MEDIO/ALTO/CRITICO
  - `temas`: Lista de temas identificados
  - `urgencia`: BAIXA/MEDIA/ALTA

**Temperatura:** 0.3 (mais determinístico)

---

#### `empathetic_response.py` (10.2 KB)
**Descrição:** Agente de resposta empática  
**Responsabilidades:**
- Gera resposta personalizada baseada em categoria NPS
- Promotor (9-10): Celebra e agradece
- Neutro (7-8): Agradece e pergunta melhorias
- Detrator (0-6): Acolhe e pede desculpas
- Suporta personalização com nome do cliente

**Temperatura:** 0.7 (mais criativo)

---

#### `message_generator.py` (12.3 KB)
**Descrição:** Gerador de mensagens proativas (não usado atualmente)  
**Responsabilidades:**
- Geração de mensagens personalizadas
- Integração com contexto do cliente

---

#### `context_collector.py` (8.7 KB)
**Descrição:** Coletor de contexto do cliente (não usado atualmente)  
**Responsabilidades:**
- Coleta dados do HubSpot
- Agregação de informações

---

#### `response_evaluator.py` (16.7 KB)
**Descrição:** Avaliador de qualidade de respostas (não usado atualmente)  
**Responsabilidades:**
- Avalia qualidade das respostas geradas
- Métricas de performance

---

#### `agents/llm/tess_llm.py` (3.3 KB)
**Descrição:** Wrapper LangChain para TessClient  
**Responsabilidades:**
- Compatibilidade com LangChain
- Interface `LLM` padrão
- Permite uso em Chains, Memory, etc.

---

### 🔧 Serviços (`/services`)

#### `cliente_service.py` (8.4 KB)
**Descrição:** Serviço de integração com HubSpot Mock  
**Responsabilidades:**
- Busca de clientes por email/username
- Coleta de contexto (deals, tickets, notes, emails)
- Cache em memória
- Cálculo de métricas (valor total, quantidade)

**Status:** Implementado, testado localmente, **não ativo em produção** (HubSpot Mock é local)

---

### 🧪 Testes

#### `test_conversacao_completa.py` (6.9 KB) ⭐
**Descrição:** Teste end-to-end completo  
**Testes:**
1. Cliente identificado (Ana Silva)
2. Cliente não identificado
3. Off-script com personalização

**Como rodar:** `python3 test_conversacao_completa.py`

---

#### `test_hubspot_integration.py` (5.5 KB)
**Descrição:** Teste integração HubSpot Mock  
**Valida:**
- Busca de clientes
- Coleta de contexto
- Métricas calculadas

---

#### `test_fluxo_completo.py` (5.2 KB)
**Descrição:** Teste fluxo completo de conversa  
**Cenários:** Promotor, Neutro, Detrator

---

#### `check_vercel_env.py` (2.7 KB) 🔍
**Descrição:** Diagnóstico de variáveis de ambiente  
**Valida:**
- Presença de todas as variáveis necessárias
- Testa conexão com Tess AI
- Útil para debug de deploy

**Como rodar:** `python3 check_vercel_env.py`

---

#### Outros Testes:
- `test_full_system.py` - Sistema completo
- `test_supabase_integration.py` - Integração Supabase
- `test_tess_direct.py` - API Tess direta
- `test_workspace_agents.py` - Agentes workspace
- `debug_tess_api.py` (v1, v2, v3) - Debug payload Tess

---

### 📄 Configuração e Deploy

#### `.env` (788 bytes)
**Descrição:** Variáveis de ambiente locais  
**Variáveis:**
```bash
TESS_API_KEY=...
TESS_DEFAULT_AGENT_ID=39004
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=...
SUPABASE_KEY=...
LANGCHAIN_API_KEY=...
```

---

#### `requirements.txt` (257 bytes)
**Descrição:** Dependências Python  
**Principais:**
- `requests>=2.31.0`
- `python-dotenv>=1.0.0`
- `supabase>=2.0.0`
- `fastapi>=0.109.0`
- `langchain>=0.1.10`
- `langsmith>=0.0.80`

---

#### `vercel.json` (282 bytes)
**Descrição:** Configuração Vercel  
**Configurações:**
- Build command
- Output directory
- Rewrites para API

---

#### `Procfile` (49 bytes)
**Descrição:** Comando para iniciar aplicação  
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

---

### 📊 SQL Schemas

#### `supabase_schema.sql` (3.4 KB)
**Descrição:** Schema principal do Supabase  
**Tabelas:**
- `nps_responses`: Avaliações NPS
- Campos: chat_id, score, feedback, sentiment, categoria, etc.

---

#### `supabase_schema_conversations.sql` (1.5 KB)
**Descrição:** Schema de conversas  
**Tabelas:**
- `conversation_messages`: Histórico de mensagens
- Campos: chat_id, role, content, timestamp

---

#### `schema.sql` (1.9 KB)
**Descrição:** Schema legado (não usado)

---

### 📝 Documentação

#### `DEPLOY.md` (3.1 KB)
**Descrição:** Guia de deploy na Vercel  
**Conteúdo:** Passo a passo, variáveis de ambiente

---

#### `AGENT_STATUS.md` (2.4 KB)
**Descrição:** Status dos agentes Tess  
**Conteúdo:** Lista de agentes, IDs, status

---

#### `RESUMO_EXECUTIVO.md` (8.8 KB)
**Descrição:** Resumo executivo do projeto  
**Conteúdo:** Visão geral, arquitetura, resultados

---

#### `FIX_VERCEL.md` (699 bytes)
**Descrição:** Fix rápido para adicionar `TESS_DEFAULT_AGENT_ID`

---

#### `VERCEL_ENV_FIX.md` (2.2 KB)
**Descrição:** Guia completo de variáveis de ambiente Vercel

---

### 🔧 Utilitários

#### `telegram_client.py` (1.9 KB)
**Descrição:** Cliente Telegram Bot API  
**Responsabilidades:**
- Envio de mensagens
- Formatação de respostas

---

#### `hubspot_client.py` (12.3 KB)
**Descrição:** Cliente HubSpot (legado, substituído por `cliente_service.py`)

---

#### `setup_supabase_conversations.py` (3.6 KB)
**Descrição:** Script de setup inicial do Supabase  
**Função:** Criar tabelas, índices

---

#### `list_available_agents.py` (2.3 KB)
**Descrição:** Lista agentes disponíveis na Tess  
**Como rodar:** `python3 list_available_agents.py`

---

#### `explore_tess_api.py` (3.7 KB)
**Descrição:** Exploração da API Tess  
**Função:** Testes manuais, experimentação

---

### 🗂️ Outros

#### `.gitignore` (40 bytes)
**Descrição:** Arquivos ignorados pelo Git  
**Ignora:** `.env`, `__pycache__`, `venv/`

---

#### `projeto-pareto.md` (6.4 KB)
**Descrição:** Cópia local do documento principal (desatualizado)  
**Nota:** Versão principal está em `Global/projeto-pareto.md`

---

## 🎯 Arquivos Críticos para Handoff

**Leitura Obrigatória:**
1. `conversation_manager.py` - Lógica principal
2. `tess_client.py` - Integração Tess (payload crítico)
3. `api.py` - Webhook Telegram
4. `agents/sentiment_analyzer.py` - Análise
5. `agents/empathetic_response.py` - Respostas

**Testes Importantes:**
1. `test_conversacao_completa.py` - End-to-end
2. `check_vercel_env.py` - Diagnóstico

**Configuração:**
1. `.env` - Variáveis locais
2. `vercel.json` - Deploy
3. `requirements.txt` - Dependências

---

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

### Arquitetura 2.0 (04/02/2026) - ✅ CONCLUÍDO E DEPLOYED
Migração de Low-Code (Make/N8N) para Code-First (Python):
- **Telegram Bot Nativo**: Implementado endpoint `/telegram/webhook` em FastAPI. Eliminada dependência do N8N.
- **Auditoria Avançada (LangSmith)**: Integrado tracing (`@traceable`) em todos os agentes para debugging granular.
- **Simplificação**: Infraestrutura reduzida para Vercel + Supabase + Telegram (sem N8N intermediário).
- **Deploy**: Bot ativo em produção (`@pareto_nps_case_mba_bot`), respondendo via webhook em `https://pareto-case-nps.vercel.app/telegram/webhook`.

**Configurações de Produção**:
- **Vercel Environment Variables**:
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT=pareto-nps-case`
  - `SUPABASE_URL`, `SUPABASE_ANON_KEY`
  - `TESS_API_KEY`, `HUBSPOT_API_KEY`
- **Webhook Configurado**: `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://pareto-case-nps.vercel.app/telegram/webhook&secret_token=pareto-secret-123`

**Problemas Resolvidos Durante Deploy**:
1. **Conflito de Versões LangChain**: Migrado para `langchain_core` exclusivamente, removendo dependência de `langchain.chains.LLMChain`.
2. **Imports Faltantes**: Adicionados `traceable`, `time`, `supabase_client` aos imports de nível superior dos agentes.
3. **Supabase Key Mismatch**: Código atualizado para aceitar tanto `SUPABASE_KEY` quanto `SUPABASE_ANON_KEY`.

### Sistema de Conversação Inteligente (04/02/2026) - ✅ IMPLEMENTADO E TESTADO

**Problema Resolvido**: Bot agora usa IA em vez de templates fixos!

**Arquivos Criados/Modificados**:
1. ✅ **`conversation_manager.py`** (NOVO - 339 linhas)
   - Máquina de estados: IDLE → WAITING_CONFIRMATION → WAITING_SCORE → COMPLETED
   - Orquestração de múltiplos agentes (SentimentAnalyzer, EmpatheticResponse, ResponseEvaluator)
   - Memória de sessão em cache (em produção, migrar para Redis)
   - Tracing completo com `@traceable` para LangSmith
   - Suporte a modo manual (gerente assume controle)

2. ✅ **`agents/empathetic_response.py`** (REFATORADO)
   - **ANTES**: Templates fixos com if/elif baseado em keywords
   - **DEPOIS**: TessLLM com prompts contextuais
   - Usa `PromptTemplate` do LangChain
   - Considera: score NPS, sentimento, histórico de conversa
   - Fallback inteligente em caso de erro

3. ✅ **`supabase_client.py`** (ATUALIZADO)
   - Novo método: `log_conversation_message()`
   - Registra todas as mensagens (user, bot, manager, system)
   - Inclui estado da conversa, score NPS, sentimento

4. ✅ **`supabase_schema_conversations.sql`** (NOVO)
   - Tabela `conversation_messages` para histórico completo
   - Índices para performance (chat_id, created_at, sender, state)
   - Suporte a modo manual (`manual_mode` flag)

5. ✅ **`api.py`** (WEBHOOK ATUALIZADO)
   - Substituída lógica linear por `ConversationManager`
   - Adicionado `@traceable` para tracing hierárquico
   - Respostas agora são contextuais e inteligentes

**Testes Locais** (04/02/2026 - 18:00):
```
✅ Teste 1 - Detrator (Score 2/10):
   Entrada: "Dou nota 2, o atendimento foi péssimo e demorado"
   Resposta IA: "Poxa, sinto muito que sua experiência conosco não 
                 tenha sido boa... 😔 Queremos muito entender o que 
                 aconteceu para poder melhorar."

✅ Teste 2 - Promotor (Score 10/10):
   Entrada: "10! Adorei tudo, a equipe é excelente!"
   Resposta IA: "Que alegria saber que você teve uma experiência tão 
                 positiva com a gente! 😊 Muito obrigado pelo seu 
                 reconhecimento e por nos dar um 10! 💙"

✅ Teste 3 - Sem Nota:
   Entrada: "oi"
   Resposta IA: "Oi! 👋 Para começarmos, digite /start e vou te fazer 
                 uma pergunta rápida sobre sua experiência com a Pareto!"

✅ Supabase: 14 mensagens registradas corretamente
✅ LangSmith: Traces hierárquicos com múltiplos nós
```

**Deploy na Vercel** (04/02/2026 - 18:03):
- ✅ Commit: `586e8c6` - "feat: intelligent bot with ConversationManager and TessLLM"
- ✅ Push: Enviado para `main`
- ✅ Build: Concluído com sucesso
- ✅ Logs: 200 OK (webhook respondendo)
- ✅ Supabase: Mensagens sendo registradas em produção

**⚠️ PROBLEMA IDENTIFICADO (04/02/2026 - 18:17):**
- Bot em produção ainda responde com **templates antigos**
- **Causa**: Vercel usando **cache do build anterior**
- **Solução**: Forçar redeploy sem cache

**Como Forçar Redeploy Sem Cache:**
1. Acesse: https://vercel.com/dashboard
2. Projeto: **pareto-case-nps**
3. Aba **"Deployments"**
4. Deployment mais recente (commit `586e8c6`)
5. Clique nos **3 pontinhos** (⋮)
6. **"Redeploy"**
7. **DESMARQUE** "Use existing Build Cache" ⚠️
8. **"Redeploy"**
9. Aguarde 2-3 min
10. Teste no Telegram: `@pareto_nps_case_mba_bot`

**Validação Pós-Redeploy:**
- [ ] Bot responde "oi" com mensagem natural (não template)
- [ ] Respostas são únicas e contextualizadas
- [ ] Logs da Vercel mostram: `"✅ Resposta empática gerada via TessLLM"`
- [ ] Supabase registra mensagens com `sender: 'bot'` diferentes
- [ ] LangSmith mostra traces com nó `Empathetic Response Generation`

**Próximos Passos** (Após Validação):
1. ✅ **Sistema Inteligente Funcionando**
2. 🔜 **Dashboard de Monitoramento**: Interface web para gerentes (Next.js + Supabase)
3. 🔜 **Documentação Final**: Fluxogramas AS-IS/TO-BE, vídeo demo, PDF consolidado

### Integração Tess AI - Arquitetura Simplificada (04/02/2026 - 20:00) - ✅ CONCLUÍDO

**Decisão Arquitetural**: Usar **agente único Tess (ID 39004)** com prompts definidos no código

**Problema Identificado**:
- Haviam 2 agentes criados na plataforma Tess com prompts configurados
- Código usava `TessLLM` (wrapper genérico) que **ignorava** os agentes da plataforma
- Duplicação: prompts na plataforma + prompts no código

**Solução Implementada**:
- ✅ Deletado agente de geração de mensagens
- ✅ Mantido apenas agente 39004 (sem prompt na plataforma)
- ✅ Todos os componentes usam `TessLLM` com prompts no código
- ✅ Migrado `SentimentAnalyzer` de `TessClient.execute_agent` para `TessLLM`

**Vantagens**:
- Prompts versionados no Git
- Fácil de ajustar (sem acessar plataforma)
- Consistência: mesma tecnologia em todos os agentes
- Deploy rápido (só código)

**Commits**:
- `dca4459` - Migração SentimentAnalyzer para TessLLM
- `c52b285` - Persona Tess + remoção de emojis
- `8bd1578` - Remoção de obrigatoriedade do /start (histórico)
- `b8603b0` - /start obrigatório + etapa de confirmação

---

## 🎯 Fase Atual - Refinamento de Prompts (04/02/2026 - 20:30)

### Objetivo
Implementar prompts refinados com personalização baseada em dados do **HubSpot Mock API**.

### HubSpot Mock API - Descobertas

**Repositório**: https://github.com/fermazim/hubspot_mockapi  
**Tecnologia**: WireMock (container Docker)  
**Porta**: 8080

**Clientes Disponíveis**:
- **101** - Cliente 1 (elegível para pesquisa - `mock_csat_survey: "true"`)
- **102** - Cliente 2 (elegível para pesquisa - `mock_csat_survey: "true"`)
- **103** - Cliente 3 (grupo controle)

**Endpoints Implementados**:
```
POST /crm/v3/objects/contacts/search   # Buscar clientes
POST /crm/v3/objects/deals/search       # Negócios fechados
POST /crm/v3/objects/tickets/search     # Tickets churn/downgrade
POST /crm/v3/objects/notes/search       # Anotações
POST /crm/v3/objects/emails/search      # E-mails
GET  /crm/v4/objects/deals/{id}/associations/line_items  # Produtos
```

**Autenticação**: `Authorization: Bearer pat-na1-123`

**Dados Disponíveis por Cliente**:
- Nome completo (`firstname`, `lastname`)
- Email, telefone
- Negócios fechados (últimos 30 dias)
- Tickets abertos
- Anotações
- E-mails trocados
- Produtos contratados (line items)

### Decisão Arquitetural - SEM Estado IDENTIFYING

**Premissa**: Assumir que todos os usuários do bot são clientes  
**Fluxo Simplificado**: `IDLE → WAITING_CONFIRMATION → WAITING_SCORE → COMPLETED`

**Estratégia de Identificação**:
1. Chat ID → Buscar no Supabase (cache)
2. Telegram Username → Buscar no HubSpot Mock (email)
3. Fallback → Continuar SEM contexto

### Prompts Refinados (8 Prompts)

#### 1. Saudação COM Contexto
- Personalizada com nome + produtos
- Temperatura: 0.7

#### 2. Saudação SEM Contexto
- Genérica mas calorosa
- Temperatura: 0.7

#### 3. Off-Script
- Responder pergunta + pedir nota
- Temperatura: 0.7

#### 4. Pedir Nota
- Inteligente, não repetitiva
- Temperatura: 0.8

#### 5. Sentiment Analysis (interno - JSON)
- **COM Contexto**: Considera histórico + tickets
- **SEM Contexto**: Apenas score + feedback
- Temperatura: 0.3

#### 6. Empathetic Response
- **COM Nome**: Usa nome do cliente
- **SEM Nome**: Usa "você"
- Temperatura: 0.7

#### 7. NPS Evaluation (interno - JSON)
- Classificação + temas + urgência
- Temperatura: 0.5

#### 8. Já Registrado
- Agradecimento personalizado
- Temperatura: 0.7

### Plano de Implementação (3.5h)

**Fase 1: Preparação (30 min)**
- Atualizar `ConversationSession` com campos `cliente_identificado` e `dados_cliente`
- Criar `ClienteService` para busca no HubSpot Mock

**Fase 2: Integração HubSpot Mock (1h)**
- Implementar busca de cliente por email
- Implementar coleta de contexto (deals, tickets, notes, emails)
- Calcular métricas (num_deals, num_tickets, valor_total)

**Fase 3: Atualizar Prompts (1.5h)**
- Atualizar `_handle_idle()` com saudação COM/SEM contexto
- Implementar `_gerar_saudacao()` com versões personalizadas
- Atualizar `empathetic_response.py` com versões COM/SEM nome
- Atualizar `sentiment_analyzer.py` com versões COM/SEM contexto

**Fase 4: Testes (30 min)**
- Teste COM contexto (cliente 101)
- Teste SEM contexto (cliente novo)
- Validar personalização

**Fase 5: Deploy (15 min)**
- Configurar variáveis de ambiente
- Commit e push
- Redeploy Vercel sem cache

### Arquivos a Criar/Modificar

**NOVOS**:
- `langchain/services/cliente_service.py` - Integração HubSpot Mock
- `langchain/services/__init__.py`

**MODIFICADOS**:
- `langchain/conversation_manager.py` - Adicionar identificação de cliente
- `langchain/agents/empathetic_response.py` - Versões COM/SEM nome
- `langchain/agents/sentiment_analyzer.py` - Versões COM/SEM contexto

### Variáveis de Ambiente Necessárias

```bash
# .env
HUBSPOT_MOCK_URL=http://seu-dominio-mock:8080
HUBSPOT_TOKEN=pat-na1-123
```

---

## Projeto Pareto - Sistema NPS Inteligente

> **Última Atualização:** 05/02/2026  
> **Status:** ✅ Sistema completo em produção (bot + backend) | ✅ Dashboard validado localmente | ⏳ Deploy do dashboard pendente  
> **Versão:** 2.3 - Dashboard MVP validado + identidade visual Pareto aplicada

---

## 📋 Resumo Executivo

Sistema de coleta e análise de NPS via Telegram Bot, utilizando **agentes inteligentes** (LangChain + Tess AI) para conversas naturais e análise de sentimento em tempo real.

**Diferenciais:**
- ✅ Bot 100% inteligente (sem templates fixos)
- ✅ Personalização com dados do cliente (HubSpot Mock)
- ✅ Análise de sentimento em tempo real
- ✅ Respostas empáticas contextualizadas
- ✅ Logs completos (Supabase + LangSmith)
- ✅ /start obrigatório para iniciar novas interações
- ✅ Persona "Tess" consistente

---

## 🚀 Status Atual (05/02/2026)

### ✅ Implementado e Testado
1. **Sistema Multi-Agente NPS** (LangChain)
2. **Bot Telegram Inteligente** (Tess AI)
3. **Persona "Tess"** (sem emojis, profissional)
4. **/start Obrigatório** (inicia novas interações)
5. **Integração Tess AI Simplificada** (agente único)
6. **Logs no Supabase** (conversas completas)
7. **Tracing no LangSmith** (auditoria visual)
8. **Deploy na Vercel** (produção ativa)
9. **Refinamento de Prompts COM Personalização**
   - `ClienteService` para HubSpot Mock
   - Identificação automática de cliente
   - Saudação personalizada (COM/SEM contexto)
   - Respostas empáticas (COM/SEM nome)
   - Testes locais: ✅ TODOS PASSARAM
10. **Dashboard de Monitoramento (Next.js)** ✅
    - Login Supabase Auth funcionando
    - Lista e histórico de conversas OK
    - Intervenção manual + retorno ao automático OK
    - Identidade visual Pareto aplicada (dark + aurora + glassmorphism)

### 📊 Commits Recentes
- `618ffe0` - feat: implement customer context personalization
- `0c41b0b` - fix: add username parameter to process_message
- `32046c8` - fix: use correct env variable names for HubSpot Mock
- `08cf9e9` - test: add HubSpot Mock integration tests ✅
- `b8603b0` - feat: add /start confirmation step
- `dd2ad09` - test: update flows for /start confirmation
- `342a695` - fix: force next builder for dashboard deploy (Vercel)

### ⏳ Próximos Passos
1. Deploy do dashboard na Vercel (root `dashboard`) e validação em produção
2. Atualizar este documento com a URL pública do dashboard
3. Fluxogramas AS-IS/TO-BE
4. Vídeo demonstrativo (2–3 min)
5. Documento PDF consolidado com screenshots e links

---

## 🏗️ Arquitetura do Sistema

### ✅ Concluído
1. Sistema multi-agente NPS com LangChain
2. Bot Telegram inteligente (sem templates)
3. Persona "Tess" implementada
4. Remoção de emojis
5. /start obrigatório (inicia novas interações)
6. Integração Tess AI simplificada (agente único)
7. Logs no Supabase
8. Tracing no LangSmith
9. Deploy na Vercel
10. **Refinamento de prompts com personalização (NOVO)**
    - ClienteService para HubSpot Mock
    - Identificação automática de cliente
    - Saudação personalizada COM/SEM contexto
    - Respostas empáticas COM/SEM nome
    - Commits: `618ffe0`, `0c41b0b`
11. **Dashboard de Monitoramento (MVP local validado)**
    - Next.js + Supabase Auth + intervenção manual
    - Identidade visual Pareto aplicada

### ⏳ Próximos Passos
11. Deploy do dashboard na Vercel + validação em produção
12. Fluxogramas AS-IS/TO-BE
13. Vídeo demonstrativo
14. Documento PDF consolidado
15. Plano de projeto com ROI

---

## 🎯 Refinamento de Prompts - Implementação Completa (04/02/2026 - 21:00)

### Objetivo Alcançado
Implementar prompts refinados com personalização baseada em dados do **HubSpot Mock API**.

### Arquivos Criados (2)

#### 1. `services/cliente_service.py` (270 linhas)
**Funcionalidades:**
- `buscar_por_email()` - Busca cliente no HubSpot Mock
- `buscar_por_chat_id()` - Busca no cache/Supabase
- `coletar_contexto()` - Coleta deals, tickets, notes, emails (últimos 30 dias)
- Cache em memória para performance
- Tratamento de erros robusto

**Exemplo de uso:**
```python
cliente = cliente_service.buscar_por_email("joao@exemplo.com")
if cliente:
    contexto = cliente_service.coletar_contexto(cliente["id"])
    # contexto contém: deals, tickets, notes, emails, metricas
```

#### 2. `services/__init__.py`
Export do singleton `cliente_service`

---

### Arquivos Modificados (2)

#### 1. `conversation_manager.py` (+150 linhas)

**Novos Campos em ConversationSession:**
```python
self.cliente_identificado: bool = False
self.dados_cliente: Optional[Dict[str, Any]] = None
```

**Novos Métodos:**

1. **`_tentar_identificar_cliente()`** (47 linhas)
   - Busca por chat_id no cache
   - Busca por username no HubSpot Mock
   - Coleta contexto completo se encontrado
   - Fallback: retorna None

2. **`_gerar_saudacao()`** (64 linhas)
   - **COM Contexto:** Usa nome do cliente
   - **SEM Contexto:** Saudação genérica
   - Gerada dinamicamente com TessLLM

**Métodos Atualizados:**

1. **`_handle_idle()`**
   - Chama `_tentar_identificar_cliente()` no início
   - Usa `_gerar_saudacao()` para boas-vindas
   - Respostas off-script COM/SEM nome

2. **`process_message()`**
   - Aceita parâmetro `username`
   - Passa para `_handle_idle()`

3. **`_generate_empathetic_response()`**
   - Passa `cliente_dados` para empathetic generator

---

#### 2. `agents/empathetic_response.py` (+70 linhas)

**Método Atualizado:**
```python
def generate_response(
    self, 
    score: int, 
    feedback_text: str = "",
    conversation_history: List[Dict] = None,
    sentiment: Dict[str, Any] = None,
    cliente_dados: Optional[Dict[str, Any]] = None  # NOVO
) -> str:
```

**Prompts Personalizados:**

**COM Nome:**
```python
prompt = f"""Você é a Tess, assistente empática da Pareto.

CONTEXTO DA AVALIAÇÃO:
- Cliente: {nome}
- Score NPS: {score}/10
- Categoria: {categoria}

TAREFA:
Escreva uma resposta NATURAL e EMPÁTICA para {nome}.

DIRETRIZES:
- Use o nome {nome} na resposta
- Sem emojis
- Máximo 3-4 linhas
"""
```

**SEM Nome:**
```python
prompt = f"""Você é a Tess, assistente empática da Pareto.

CONTEXTO DA AVALIAÇÃO:
- Score NPS: {score}/10
- Categoria: {categoria}

TAREFA:
Escreva uma resposta NATURAL e EMPÁTICA.

DIRETRIZES:
- Sem emojis
- Máximo 3-4 linhas
"""
```

---

### Funcionalidades Implementadas

#### 1. Identificação Automática ✅
- Busca por `chat_id` no cache
- Busca por `username` no HubSpot Mock
- Coleta contexto completo (deals, tickets, notes, emails)
- Armazena na sessão

#### 2. Saudação Personalizada ✅
**COM Contexto:**
```
"Olá, João! Aqui é a Tess, da equipe de qualidade da Pareto. 
Fico feliz em falar com você! Em uma escala de 0 a 10, 
quanto você recomendaria nossos serviços?"
```

**SEM Contexto:**
```
"Olá! Sou a Tess, assistente de qualidade da Pareto.
Queremos saber como foi sua experiência recente conosco. 
Em uma escala de 0 a 10, quanto você recomendaria nossos serviços?"
```

#### 3. Respostas Off-Script Personalizadas ✅
**COM Nome:**
```
Usuário: "como assim?"
Bot: "Deixe-me explicar, João. Estou coletando feedback sobre 
     sua experiência com a Pareto..."
```

**SEM Nome:**
```
Usuário: "como assim?"
Bot: "Deixe-me explicar. Estou coletando feedback sobre 
     sua experiência com a Pareto..."
```

#### 4. Resposta Empática Personalizada ✅
**COM Nome:**
```
Usuário: "Dou nota 9, adorei!"
Bot: "Que alegria, João! Muito obrigada pelo reconhecimento..."
```

**SEM Nome:**
```
Usuário: "Dou nota 9, adorei!"
Bot: "Que alegria saber disso! Muito obrigada pelo reconhecimento..."
```

#### 5. Fallback Inteligente ✅
- Se HubSpot Mock offline: continua SEM contexto
- Se cliente não encontrado: usa prompts genéricos
- Zero impacto na experiência

---

### Commits Realizados

**Commit 1:** `618ffe0`
```
feat: implement customer context personalization with HubSpot Mock

- Created ClienteService for HubSpot Mock integration
- Added cliente_identificado and dados_cliente to ConversationSession
- Implemented _tentar_identificar_cliente() with email/username search
- Created _gerar_saudacao() with COM/SEM contexto versions
- Updated empathetic_response.py to accept cliente_dados
- Personalized prompts use customer name when available
- Fallback to generic prompts when customer not identified
```

**Commit 2:** `0c41b0b`
```
fix: add username parameter to process_message for customer identification
```

---

### Testes Pendentes

#### Teste 1: Cliente Identificado
- [ ] Configurar HubSpot Mock localmente
- [ ] Testar com cliente 101
- [ ] Validar saudação com nome
- [ ] Validar resposta empática com nome

#### Teste 2: Cliente NÃO Identificado
- [ ] Testar com username desconhecido
- [ ] Validar saudação genérica
- [ ] Validar resposta empática genérica

#### Teste 3: Fallback
- [ ] Desligar HubSpot Mock
- [ ] Validar funcionamento SEM contexto
- [ ] Verificar logs de erro

---

### Deploy Pendente

**Variáveis de Ambiente:**
```bash
HUBSPOT_MOCK_URL=http://seu-dominio:8080
HUBSPOT_TOKEN=pat-na1-123
```

**Passos:**
1. Adicionar variáveis no Vercel
2. Redeploy SEM CACHE
3. Testar em produção

---

## 🎯 Fase Final - Dashboard de Monitoramento (04/02/2026)

### Requisito Crítico da Pareto
**Interface de Monitoramento** para Gerentes de Qualidade com:
- ✅ **Supervisão em tempo real** de conversas ativas
- ✅ **Histórico completo** de todas as interações
- ✅ **Intervenção manual** - Gerente pode assumir controle da conversa

### Arquitetura Escolhida: 100% Free Tier

**Stack Tecnológica** (Custo: $0):
```
Frontend:  Next.js (Vercel Free Tier)
Backend:   FastAPI (já rodando na Vercel)
Database:  Supabase PostgreSQL (Free: 500MB)
Realtime:  Supabase Realtime WebSocket (Free: 200 conexões)
Auth:      Supabase Auth (Free, incluído)
Deploy:    Vercel (Free para projetos acadêmicos)
```

**Justificativa**: Manter 100% gratuito como todo o projeto (Vercel, Supabase, Telegram, LangSmith).

**Atualização (05/02/2026):** MVP concluído e validado localmente em `langchain/dashboard` (Next.js + Supabase Auth + telas de lista/detalhe/intervenção), com identidade visual Pareto aplicada (dark + aurora + glassmorphism). Intervenção manual e retorno ao automático funcionando; envio manual chega no Telegram. Fix de deploy adicionado: `dashboard/vercel.json` força builder `@vercel/next` e evita erro de Output Directory.

### Componentes do Dashboard

#### 1. Tela Principal - Lista de Conversas
- Listagem em tempo real de todas as conversas
- Filtros: Data, Score NPS, Sentimento, Status
- Indicadores visuais: 🟢 Promotor | 🟡 Neutro | 🔴 Detrator
- Atualização automática via Supabase Realtime

#### 2. Visualização de Conversa Individual
- Histórico completo de mensagens (usuário + bot)
- Metadados: Score NPS, Sentimento, Duração
- Timeline com timestamps
- Estado da conversa (IDLE, WAITING_CONFIRMATION, WAITING_SCORE, WAITING_FEEDBACK, COMPLETED)

#### 3. Modo de Intervenção Manual
- Botão **"Assumir Controle"** em conversas ativas
- Campo de texto para gerente digitar mensagem
- Envio via endpoint `/telegram/send-manual`
- Flag `manual_mode` no banco para pausar bot automático
- Botão **"Retornar ao Automático"**

#### 4. Dashboard de Métricas
- NPS médio geral
- Distribuição: % Promotores, Neutros, Detratores
- Total de conversas (hoje, semana, mês)
- Taxa de resposta
- Tempo médio de conversa

### Implementação Técnica

#### Nova Tabela Supabase
```sql
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id TEXT NOT NULL,
    message_text TEXT NOT NULL,
    sender TEXT CHECK (sender IN ('user', 'bot', 'manager')),
    conversation_state TEXT,
    nps_score INTEGER,
    sentiment TEXT,
    manual_mode BOOLEAN DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Novo Endpoint API
```python
@app.post("/telegram/send-manual")
async def send_manual_message(chat_id: str, message: str, manager_id: str):
    """Permite gerente enviar mensagem manual via dashboard"""
    # 1. Ativar flag manual_mode
    # 2. Enviar mensagem via Telegram
    # 3. Logar no Supabase com sender='manager'
```

#### Frontend (Next.js)
```javascript
// Realtime subscription para atualização automática
supabase
  .channel('conversations')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'conversation_messages' },
    (payload) => updateUI(payload)
  )
  .subscribe()
```

#### Como rodar o dashboard localmente
```bash
cd /Users/julianamoraesferreira/Documents/Projetos-Dev-Petrick/pareto-case/langchain/dashboard
npm install
npm run dev
```

**Variáveis necessárias (`.env.local`):**
```bash
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_BASE_URL=https://pareto-case-nps.vercel.app
```

### Estrutura de Diretórios
```
pareto-case/
├── langchain/          # Backend FastAPI (existente)
│   └── dashboard/      # Frontend Next.js (NOVO)
│       ├── app/
│       │   ├── page.tsx           # Lista de conversas
│       │   ├── conversation/[id]/ # Visualização individual
│       │   └── metrics/           # Dashboard de métricas
│       ├── components/
│       │   ├── ConversationList.tsx
│       │   ├── MessageThread.tsx
│       │   └── ManualControl.tsx
│       └── lib/
│           └── supabase.ts        # Cliente Supabase
└── Global/             # Documentação (existente)
```

---

## ✅ Relatório de Validação Local (05/02/2026)

### Configuração do Dashboard
- Arquivo criado: `langchain/dashboard/.env.local` (não versionado)
- Variáveis:
```env
NEXT_PUBLIC_SUPABASE_URL=https://dqczihjtuujoqwkdpjgf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<SUPABASE_ANON_KEY>
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Supabase Auth
- Usuário criado: `gestor@pareto.com`
- Senha definida localmente (não versionada)

### Validação do Sistema
**Backend (FastAPI):**
- ✅ Rodando em `http://localhost:8000`
- ✅ Endpoints disponíveis: `/health`, `/contacts`, `/nps/*`, `/telegram/webhook`
- ⚠️ Warning de Pydantic v1 + Python 3.14 (não afeta funcionamento)

**Dashboard (Next.js):**
- ✅ Rodando em `http://localhost:3001` (porta 3000 ocupada)
- ✅ Carregou variáveis do `.env.local`
- ✅ Conectou ao Supabase com sucesso
- ✅ Login funcionando com usuário criado
- ✅ Listando conversas de teste:
  - `test_inteligencia_003` (idle)
  - `test_promotor_002` (completed)
  - `test_detrator_001` (completed)
- ✅ Identidade visual Pareto aplicada (dark + aurora + glassmorphism) e aprovada

### Validação Funcional (concluída)
- [x] Clicar em conversa e ver histórico completo
- [x] Testar "Assumir controle"
- [x] Testar "Enviar mensagem manual"
- [x] Testar "Retornar ao automático"
- [x] Verificar se mensagem manual chega no Telegram

### Pendências de Commit (resolvidas)
- [x] `.env.local` ignorado no `.gitignore` (não versionar chaves)
- [x] Commitados: `FIX_VERCEL.md`, `VERCEL_ENV_FIX.md`, `check_vercel_env.py`, `test_conversacao_completa.py`, `debug_tess_api*.py`, `dashboard/vercel.json`
- [x] Não rodar `npm audit fix --force`

---

## 🚀 Instruções para Deploy do Dashboard na Vercel (05/02/2026)

### Passo 1: Criar novo projeto
1. Acesse: https://vercel.com/dashboard  
2. **Add New** → **Project**  
3. Repositório: `petrickramos/pareto-case-nps`  
4. **Root Directory**: `dashboard` *(repo root já é `langchain`)*  
5. **Project Name**: `pareto-nps-dashboard`  
6. **Framework Preset**: Next.js (auto)  
7. **Output Directory**: vazio/default  

> **Se ocorrer erro “No Output Directory named public”**: confirmar que existe `dashboard/vercel.json` (com `@vercel/next`) e fazer redeploy sem cache.

### Passo 2: Variáveis de ambiente
Adicionar em **Production**, **Preview** e **Development**:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://dqczihjtuujoqwkdpjgf.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `<SUPABASE_ANON_KEY>` |
| `NEXT_PUBLIC_API_BASE_URL` | `https://pareto-case-nps.vercel.app` |

> **Nota:** usar a anon key do Supabase (pública). Não usar `service_role`.

### Passo 3: Deploy
1. Clique em **Deploy**  
2. Aguarde o build  
3. URL esperada: `https://pareto-nps-dashboard.vercel.app`

### Passo 4: Teste pós-deploy
- [ ] Login com `gestor@pareto.com`  
- [ ] Lista de conversas carrega  
- [ ] Histórico abre  
- [ ] Assumir controle  
- [ ] Enviar mensagem manual  
- [ ] Retornar ao automático  

---

## 🔜 Próximas Etapas Imediatas (05/02/2026)
1. Finalizar o deploy do dashboard na Vercel (com `dashboard/vercel.json` já versionado).  
2. Validar todas as funcionalidades em produção (login, histórico, intervenção manual, retorno automático).  
3. Registrar a URL final do dashboard e atualizar este documento com o link público.  
4. Capturar screenshots do dashboard para o PDF final.  
5. Gravar vídeo demonstrativo (2–3 min) com Telegram + dashboard + LangSmith + Supabase.  

---

## 📦 Entregas Finais Pendentes

### 1. Fluxogramas (AS-IS & TO-BE)
- [ ] Criar fluxograma processo manual atual
- [ ] Criar fluxograma processo automatizado
- [ ] Exportar em formato visual (PNG/PDF)

### 2. Vídeo Demonstrativo
- [ ] Gravar conversa completa no Telegram
- [ ] Mostrar dashboard em ação (tempo real)
- [ ] Demonstrar intervenção manual
- [ ] Navegar no LangSmith (grafos)
- [ ] Consultar Supabase (auditoria)
- **Duração**: 2-3 minutos

### 3. Documento PDF Consolidado
Estrutura:
- Capa e introdução
- Fluxogramas AS-IS e TO-BE
- Arquitetura técnica completa
- Descrição dos agentes + prompts
- Screenshots do dashboard
- Prints do LangSmith (grafos)
- Transcrições de conversas de teste
- Plano de projeto com ROI
- Links públicos (GitHub, agentes Tess, dashboard)

### 4. Plano de Projeto com ROI
- [ ] Fases de implementação
- [ ] Atividades-chave por fase
- [ ] Estimativa de esforço
- [ ] Cálculo de ROI:
  - Tempo economizado: 30min → 2min por cliente
  - Custo/hora gerente vs custo infraestrutura
  - Escalabilidade (1 gerente → 100+ clientes/dia)

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

---

## 🔄 HANDOFF - Informações para Continuidade do Projeto

> **Data:** 04/02/2026 - 21:48  
> **Status:** ✅ Implementação de Personalização Completa | Pronto para Deploy  
> **Última Implementação:** Refinamento de Prompts com HubSpot Mock

---

### 📦 O QUE ESTÁ PRONTO

#### ✅ Código Implementado e Testado

**1. Sistema Multi-Agente NPS**
- Localização: `/langchain/`
- Arquivos principais:
  - `conversation_manager.py` - Orquestrador principal ⭐
  - `agents/sentiment_analyzer.py` - Análise de sentimento
  - `agents/empathetic_response.py` - Respostas empáticas (COM/SEM nome) ⭐
  - `agents/llm/tess_llm.py` - Wrapper Tess AI
  - `services/cliente_service.py` - Integração HubSpot Mock ⭐ NOVO

**2. Bot Telegram**
- Endpoint: `/telegram/webhook` em `api.py`
- Funcionalidades:
  - ✅ Requer /start para iniciar nova interação
  - ✅ Extrai nota NPS (0-10) automaticamente
  - ✅ Respostas 100% geradas por IA (sem templates)
  - ✅ Persona "Tess" consistente (sem emojis)
  - ✅ Personalização COM/SEM contexto do cliente ⭐ NOVO

**3. Personalização com HubSpot Mock** ⭐ NOVO
- Arquivo: `services/cliente_service.py`
- Funcionalidades:
  - Busca cliente por email/username
  - Coleta contexto (deals, tickets, notes, emails)
  - Cache em memória
  - Fallback inteligente se cliente não encontrado

**Exemplo de Personalização:**
```python
# COM contexto (cliente identificado)
"Que alegria, Ana! Muito obrigada pelo reconhecimento."

# SEM contexto (cliente não identificado)
"Que alegria saber disso! Muito obrigada pelo reconhecimento."
```

**4. Testes de Integração** ⭐ NOVO
- Arquivo: `test_hubspot_integration.py`
- Status: ✅ **TODOS OS 4 TESTES PASSARAM**
  - Teste 1: Conectividade HubSpot Mock ✅
  - Teste 2: Busca de cliente por email ✅
  - Teste 3: Coleta de contexto (deals, tickets, notes, emails) ✅
  - Teste 4: Simulação de personalização ✅

**Resultado dos Testes:**
```
✅ Cliente "Ana Silva" (ID 101) identificado
✅ Contexto coletado: 2 deals, R$ 15.500
✅ Personalização: "Que alegria, Ana!"
```

---

### 📊 COMMITS IMPORTANTES (Últimos 4)

**1. `618ffe0` - feat: implement customer context personalization**
- Criado `ClienteService` para HubSpot Mock
- Adicionados campos `cliente_identificado` e `dados_cliente` na sessão
- Implementado `_tentar_identificar_cliente()`
- Criado `_gerar_saudacao()` COM/SEM contexto
- Atualizado `empathetic_response.py` para aceitar `cliente_dados`

**2. `0c41b0b` - fix: add username parameter to process_message**
- Adicionado parâmetro `username` em `process_message()`
- Passa username para `_handle_idle()` para identificação

**3. `32046c8` - fix: use correct env variable names for HubSpot Mock**
- Suporte para `HUBSPOT_API_URL` e `HUBSPOT_MOCK_URL`
- Suporte para `HUBSPOT_API_KEY` e `HUBSPOT_TOKEN`
- Fallback chain para compatibilidade

**4. `08cf9e9` - test: add HubSpot Mock integration tests** ✅
- Criado `test_hubspot_integration.py`
- 4 testes abrangentes
- Todos passando

---

### 🔧 COMO RODAR LOCALMENTE

**Pré-requisitos:**
```bash
# Instalar dependências
cd langchain
pip install -r requirements.txt

# Verificar .env (já existe)
# Variáveis em /langchain/.env
```

**Rodar HubSpot Mock (Opcional - Para Testes):**
```bash
# Iniciar Docker
cd hubspot-mockapi
docker-compose up -d

# Verificar se está rodando
docker ps | grep mock

# Testar integração
cd ../langchain
python3 test_hubspot_integration.py
```

**Rodar Bot Localmente:**
```bash
cd langchain
python3 api.py

# Testar endpoint
curl http://localhost:8000/health
```

---

### 🚀 DEPLOY

**Status Atual:**
- ✅ Código no GitHub: `main` branch atualizada
- ✅ Vercel: Deploy ativo (sem HubSpot Mock)
- ⏳ Próximo Deploy: Com fallback genérico

**Como Fazer Deploy:**
```bash
# 1. Verificar que código está no GitHub
git status
git push origin main

# 2. Acessar Vercel: https://vercel.com/dashboard
# 3. Projeto: pareto-case-nps
# 4. Deployments → Último → ⋮ → Redeploy
# 5. ⚠️ DESMARCAR "Use existing Build Cache"
# 6. Redeploy
```

**Variáveis de Ambiente (Vercel):**

Já Configuradas:
- `TELEGRAM_BOT_TOKEN`
- `TESS_API_KEY`
- `TESS_DEFAULT_AGENT_ID`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `LANGCHAIN_API_KEY`

Opcionais (HubSpot Mock - Apenas Local):
- `HUBSPOT_API_URL` - URL do HubSpot Mock (local: http://localhost:4010)
- `HUBSPOT_API_KEY` - Token (mock: pat-na1-123)

**⚠️ Nota Importante:** HubSpot Mock NÃO funciona na Vercel (apenas local). Em produção, o bot usa fallback genérico.

---

### 📁 ESTRUTURA DE ARQUIVOS

```
pareto-case/
├── langchain/
│   ├── api.py                          # FastAPI + Webhook Telegram
│   ├── conversation_manager.py         # Orquestrador principal ⭐
│   ├── supabase_client.py              # Cliente Supabase
│   ├── .env                            # Variáveis de ambiente
│   ├── requirements.txt                # Dependências Python
│   ├── test_hubspot_integration.py     # Testes HubSpot Mock ⭐ NOVO
│   ├── agents/
│   │   ├── sentiment_analyzer.py       # Análise de sentimento
│   │   ├── empathetic_response.py      # Respostas empáticas ⭐
│   │   └── llm/
│   │       └── tess_llm.py             # Wrapper Tess AI
│   └── services/                       # ⭐ NOVO
│       ├── __init__.py
│       └── cliente_service.py          # Integração HubSpot Mock
├── hubspot-mockapi/                    # HubSpot Mock (Docker)
│   ├── docker-compose.yml
│   └── wiremock/
└── Global/
    └── projeto-pareto.md               # Este arquivo
```

---

---

## 🔄 STATUS ATUAL DO PROJETO (04/02/2026 - 23:30)

### ✅ Implementações Concluídas

#### 1. Correção Crítica: Erro 422 da API Tess
**Problema Identificado:**
- Bot retornava sempre fallback "Olá! Como posso ajudar você hoje?"
- API Tess rejeitava payload com erro 422 Unprocessable Entity

**Causa Raiz:**
- Endpoint OpenAI-compatible (`/agents/{id}/openai/chat/completions`) exige:
  - `temperature`: **inteiro** (0 ou 1), não aceita floats como 0.7
  - `max_tokens`: obrigatório
  - `tools`: string obrigatória ("no-tools", "internet", etc.)

**Solução Aplicada:**
```python
# tess_client.py - linha 87-95
safe_temp = 1 if temperature > 0.5 else 0

payload = {
    "messages": messages,
    "tools": "no-tools",
    "stream": False,
    "temperature": safe_temp,  # Convertido para int
    "max_tokens": max_tokens
}
```

**Commits:**
- `f052008` - "debug: add detailed error logging to tess_client"
- `32046c8` - "fix: use correct env variable names for HubSpot Mock"

---

#### 2. Testes Locais com HubSpot Mock

**Configuração:**
- Docker container `mockhubspot` rodando na porta 4010
- Dados mock: clientes 101 (Ana Silva), 102, 103
- Integração testada com `test_conversacao_completa.py`

**Resultados:**
- ✅ **Cliente Identificado:** Bot identifica Ana Silva e personaliza ("Oi, Ana!")
- ✅ **Off-Script Personalizado:** Responde perguntas usando nome do cliente
- ⚠️ **Cliente Não Identificado:** Mock retorna sempre cliente 101 (limitação do mock)

**Métricas Coletadas:**
- Deals: 2 negócios (R$ 15.500 total)
- Tickets: 2 tickets
- Notes: 2 anotações
- Emails: 2 e-mails

---

#### 3. Refinamento de Prompts com Personalização

**Implementação Completa:**
- `ClienteService` criado em `services/cliente_service.py`
- Busca por email/username no HubSpot Mock
- Coleta de contexto (deals, tickets, notes, emails)
- Prompts COM e SEM personalização

**Fluxo de Identificação:**
```
1. Chat ID → Supabase (cache)
2. Telegram Username → HubSpot (email)
3. Fallback → Continuar SEM contexto
```

**Arquivos Modificados:**
- `conversation_manager.py`: método `_tentar_identificar_cliente()`
- `services/cliente_service.py`: integração HubSpot Mock
- `agents/empathetic_response.py`: respostas COM/SEM nome
- `agents/sentiment_analyzer.py`: análise COM/SEM contexto

---

### 🚧 Problemas em Produção (Vercel)

#### Problema Atual: Bot Retorna Fallback em Produção

**Sintoma:**
- Bot responde sempre "Olá! Como posso ajudar você hoje?"
- Logs Vercel mostram 200 OK no webhook
- Mas respostas não são inteligentes

**Diagnóstico Realizado:**

1. **Variáveis de Ambiente:**
   - ✅ `TESS_API_KEY` configurada
   - ✅ `TESS_DEFAULT_AGENT_ID=39004` adicionada (04/02 23:15)
   - ✅ `SUPABASE_KEY` configurada (código aceita `SUPABASE_KEY` ou `SUPABASE_ANON_KEY`)
   - ✅ `TELEGRAM_BOT_TOKEN` configurada
   - ✅ `LANGCHAIN_API_KEY` configurada

2. **Logging Melhorado:**
   - Adicionado logging detalhado em `tess_client.py` (commit `f052008`)
   - Captura status HTTP e corpo da resposta
   - Redeploy realizado (04/02 23:35)

**✅ RESOLVIDO (04/02 23:39):**
- Bot agora responde corretamente em produção
- API Tess funcionando após correção do payload
- Respostas inteligentes sendo geradas
- Exemplo de conversa:
  - User: "que legal"
  - Bot: "Que bom que gostou! Para nos ajudar a melhorar ainda mais, poderia nos dar uma nota de 0 a 10 sobre sua experiência?"
  - User: "meu nome é Pedro"
  - Bot: "Olá, Pedro! Entendido. Para que eu possa registrar, de 0 a 10, qual a sua nota para o nosso atendimento?"

**⚠️ Refinamentos Necessários:**
1. **Prompts precisam de ajuste:**
   - Respostas muito longas (3-4 linhas quando deveria ser 2)
   - Tom pode ser mais natural e menos formal
   - Personalização com nome do cliente ainda não está ativa em produção (HubSpot Mock é local)

2. **Fluxo de conversa:**
   - Bot está insistindo muito em pedir nota
   - Poderia ser mais sutil na transição
   - Validação de score NPS precisa ser mais robusta

---

### 📁 Estrutura Git do Projeto

**⚠️ IMPORTANTE - Descoberta Crítica:**

O repositório Git está **dentro da pasta `langchain/`**, não na raiz do projeto!

```
pareto-case/
├── Global/                    # Documentação (NÃO versionado)
├── hubspot-mockapi/          # Mock HubSpot (NÃO versionado)
├── n8n/                      # Workflows n8n (NÃO versionado)
└── langchain/                # ← REPOSITÓRIO GIT AQUI!
    ├── .git/
    ├── .env
    ├── api.py
    ├── conversation_manager.py
    └── ...
```

**Comandos Git Corretos:**
```bash
# ❌ ERRADO (raiz do projeto)
cd /Users/.../pareto-case
git add langchain/tess_client.py  # Não funciona!

# ✅ CORRETO (dentro de langchain/)
cd /Users/.../pareto-case/langchain
git add tess_client.py
git commit -m "mensagem"
git push origin main  # Branch é 'main', não 'master'
```

**Branch Ativa:** `main` (não `master`)  
**Remote:** `origin` → https://github.com/petrickramos/pareto-case-nps.git

---

### 🧪 Scripts de Teste Criados

**Testes Locais:**
- `test_conversacao_completa.py` - End-to-end com personalização
- `test_hubspot_integration.py` - Integração HubSpot Mock
- `check_vercel_env.py` - Verificar variáveis de ambiente
- `debug_tess_api.py` - Debug payload API Tess (v1, v2, v3)

**Guias de Deploy:**
- `FIX_VERCEL.md` - Adicionar TESS_DEFAULT_AGENT_ID
- `VERCEL_ENV_FIX.md` - Guia completo de variáveis

---

### 📚 Documentação Atualizada

**Novos Documentos:**
- `Global/documentacao-api-tess.md` - Guia completo da API Tess
  - Endpoints principais
  - Formato de payload OpenAI-compatible
  - Boas práticas
  - Troubleshooting
  - Referência para debug futuro

**Link Adicionado em `projeto-pareto.md`:**
```markdown
- **Documentação API Tess:** [`Global/documentacao-api-tess.md`](./documentacao-api-tess.md)
```

---

### 🎯 PRÓXIMOS PASSOS (Prioridade)

**1. Debug Produção (URGENTE - 30 min)**
- [x] Adicionar logging detalhado em `tess_client.py`
- [x] Push para GitHub (commit `f052008`)
- [ ] Redeploy na Vercel SEM CACHE
- [ ] Testar bot no Telegram
- [ ] Analisar logs detalhados
- [ ] Identificar e corrigir erro real

**2. Validação Completa (1h)**
- [ ] Confirmar respostas inteligentes no Telegram
- [ ] Validar logs no LangSmith
- [ ] Verificar persistência no Supabase
- [ ] Testar diferentes cenários (Promotor/Neutro/Detrator)

**3. Dashboard de Monitoramento (4-6h)**
- [x] Criar projeto Next.js em `/langchain/dashboard`
- [ ] Conectar com Supabase
- [ ] Listar conversas ativas
- [ ] Visualizar histórico completo
- [ ] Permitir intervenção manual

**4. Documentação Final (2-3h)**
- [ ] Criar fluxogramas AS-IS/TO-BE
- [ ] Gravar vídeo demonstrativo (2-3 min)
- [ ] Criar documento PDF consolidado
- [ ] Preparar plano de projeto com ROI

---

### 🐛 TROUBLESHOOTING ATUALIZADO

#### Problema: Bot não responde no Telegram
**Solução:**
1. Verificar logs da Vercel (Functions → procurar "Erro ao gerar texto")
2. Testar endpoint `/health`
3. Verificar webhook configurado no Telegram
4. Redeploy sem cache

#### Problema: Erro 422 da API Tess
**Causa:** Payload com `temperature` float ou faltando `max_tokens`  
**Solução:** Já corrigido em `tess_client.py` (commit `f052008`)

#### Problema: Git não funciona
**Causa:** Repositório está em `langchain/`, não na raiz  
**Solução:**
```bash
cd langchain/  # Entrar na pasta correta
git add arquivo.py
git commit -m "mensagem"
git push origin main  # Branch é 'main'
```

#### Problema: Erro ao buscar HubSpot Mock
**Solução:**
- HubSpot Mock só funciona localmente (Docker)
- Em produção, bot usa fallback genérico
- Verificar se Docker está rodando: `docker ps | grep mock`

#### Problema: Testes falhando
**Solução:**
```bash
# Instalar dependências
pip install --break-system-packages -r requirements.txt

# Verificar HubSpot Mock rodando
docker ps | grep mock

# Rodar testes
python3 test_conversacao_completa.py
```

---

### 💡 DICAS PARA CONTINUIDADE

**Antes de Começar:**
- Ler seção "STATUS ATUAL DO PROJETO" acima
- Revisar commits recentes em `langchain/`
- Rodar testes localmente (`test_conversacao_completa.py`)
- Consultar `Global/documentacao-api-tess.md` para debug

**Ao Fazer Mudanças:**
- Sempre testar localmente primeiro
- **Entrar em `langchain/`** antes de usar git
- Fazer commits pequenos e descritivos
- Documentar decisões importantes neste arquivo

**Antes de Deploy:**
- Rodar todos os testes
- Verificar logs localmente
- Fazer redeploy SEM CACHE na Vercel
- Testar no Telegram após deploy
- Verificar logs detalhados na Vercel

**Comandos Git Corretos:**
```bash
cd /Users/.../pareto-case/langchain  # ← IMPORTANTE!
git status
git add arquivo.py
git commit -m "mensagem descritiva"
git push origin main
```

---

### 📚 LINKS ÚTEIS

- **GitHub:** https://github.com/petrickramos/pareto-case-nps
- **Vercel:** https://vercel.com/dashboard
- **Supabase:** https://dqczihjtuujoqwkdpjgf.supabase.co
- **LangSmith:** https://smith.langchain.com/
- **Telegram Bot:** @pareto_nps_case_mba_bot
- **Documentação API Tess:** [`Global/documentacao-api-tess.md`](./documentacao-api-tess.md) (Guia completo para debug)
- **🔄 Handoff para Próximo Dev:** [`Global/HANDOFF.md`](./HANDOFF.md) (Guia completo de continuidade)

---

## 🧠 Engenharia de Prompt — Planejamento (05/02/2026)

### Premissas
- **/start obrigatório** para iniciar novas interações no Telegram.
- A conversa deve iniciar com uma **saudação clara + convite para feedback**.
- O bot deve entender **"sim", "não" e dúvidas** (ex.: "Como atribuo?", "como faço isso?").

### Saudação Base (Nova)
```
Olá! Tudo bem?

Sou a Tess, assistente de qualidade da Pareto.

Gostaríamos muito de saber como foi a sua experiência conosco, posso te dar mais detalhes sobre como deixar seu feedback?
```

### Respostas Esperadas

**1) Usuário confirma (sim/ok/pode)**
```
Maravilha! Por favor, atribua uma nota de 0 a 10 sobre a sua experiência usando a Tess.
```

**2) Usuário pede detalhes ("Como atribuo?", "como faço isso?")**
```
Entendi, basta digitar no teclado do celular mesmo uma nota de 0 a 10 sobre a sua experiência usando a Tess.
```

**3) Usuário recusa ("não", "agora não")**
```
Sem problemas! Quando quiser participar, é só digitar /start novamente.
```

### Fluxo Conversacional (TO-BE)
1. **/start** → enviar Saudação Base
2. **Aguardar resposta** (sim / dúvida / não)
3. **Se sim** → pedir nota (0–10)
4. **Se dúvida** → explicar como enviar nota → voltar a pedir nota
5. **Se não** → encerrar com saída gentil
6. **Se off-script** → responder e retomar convite à nota

### Plano de Implementação (Prompt + Lógica)
**Fase 1 — Modelagem de Estados (30–45 min)**
- Criar estado intermediário: `WAITING_CONFIRMATION` (ou `WAITING_CONSENT`)
- Ajustar transições: `IDLE → WAITING_CONFIRMATION → WAITING_SCORE → COMPLETED`

**Fase 2 — Prompts e Intenções (45–60 min)**
- Atualizar prompt de saudação com texto novo
- Mapear intenções: `CONFIRMA`, `DUVIDA`, `RECUSA`, `OFFSCRIPT`
- Definir respostas canônicas (3 acima)

**Fase 3 — Atualização de Lógica (45–60 min)**
- Implementar reconhecimento de intenção na resposta do usuário
- Garantir fallback seguro para dúvidas recorrentes

**Fase 4 — Testes (30 min)**
- Cenário 1: /start → "sim" → nota
- Cenário 2: /start → "Como atribuo?" → explicação → nota
- Cenário 3: /start → "não" → encerramento

### Arquivos Prováveis a Modificar
- `langchain/conversation_manager.py` (estado e roteamento)
- `langchain/agents/empathetic_response.py` (ajuste de tom, se necessário)
- `Global/projeto-pareto.md` (documentação)

---

## Contatos
- **Desenvolvedor:** Juliana Moraes Ferreira (Petrick)
- **Instituição:** MBA AI Leader - Faculdade Mar Atlântico
- **Projeto:** Case Pareto - Sistema NPS Multi-Agente
- **Última Atualização:** 04/02/2026 - 23:40
- **Versão:** 2.2 - Bot Funcionando, Aguardando Refinamento
- **📄 Handoff:** Ver [`HANDOFF.md`](./HANDOFF.md) para continuidade
