# 🔧 Guia: Configurar Variáveis de Ambiente na Vercel

## Problema Identificado

O bot está retornando sempre "Olá! Como posso ajudar você hoje?" porque **faltam variáveis de ambiente** na Vercel.

---

## ✅ Variáveis que Precisam Ser Adicionadas

### 1. TESS_DEFAULT_AGENT_ID
**Valor:** `39004`  
**Descrição:** ID do agente Tess AI usado para gerar respostas

### 2. SUPABASE_ANON_KEY
**Valor:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxY3ppaGp0dXVqb3F3a2RwamdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwOTE0NTYsImV4cCI6MjA4NTY2NzQ1Nn0.G4R74rjvQNUOb79FnwR2e3oxHPxxUW35H4L243AF-wk`  
**Descrição:** Chave anônima do Supabase para salvar logs

---

## 📝 Passo a Passo na Vercel

### 1. Acessar Dashboard
- Vá para: https://vercel.com/dashboard
- Selecione o projeto: **pareto-case-nps**

### 2. Ir para Settings
- Clique em **Settings** (no menu superior)
- No menu lateral, clique em **Environment Variables**

### 3. Adicionar Variáveis

**Variável 1:**
- **Key:** `TESS_DEFAULT_AGENT_ID`
- **Value:** `39004`
- **Environment:** Marque todas (Production, Preview, Development)
- Clique em **Save**

**Variável 2:**
- **Key:** `SUPABASE_ANON_KEY`
- **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxY3ppaGp0dXVqb3F3a2RwamdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwOTE0NTYsImV4cCI6MjA4NTY2NzQ1Nn0.G4R74rjvQNUOb79FnwR2e3oxHPxxUW35H4L243AF-wk`
- **Environment:** Marque todas (Production, Preview, Development)
- Clique em **Save**

### 4. Redeploy
- Vá para **Deployments**
- Clique nos 3 pontos (⋮) do último deployment
- Selecione **Redeploy**
- ⚠️ **IMPORTANTE:** Desmarque "Use existing Build Cache"
- Clique em **Redeploy**

---

## ✅ Verificação

Após o redeploy, teste o bot no Telegram:
1. Envie qualquer mensagem
2. O bot deve responder de forma inteligente (não mais o fallback genérico)
3. Verifique os logs na Vercel (devem mostrar chamadas à API Tess)

---

## 🐛 Se Ainda Não Funcionar

Verifique os logs da Vercel:
1. Vá em **Deployments**
2. Clique no deployment ativo
3. Vá em **Functions**
4. Procure por erros relacionados a `tess_client.py`

---

**Última Atualização:** 04/02/2026 - 23:08
