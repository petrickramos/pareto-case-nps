# 🔧 Fix: Adicionar TESS_DEFAULT_AGENT_ID na Vercel

## Problema
Bot retorna sempre "Olá! Como posso ajudar você hoje?" porque falta a variável `TESS_DEFAULT_AGENT_ID`.

## Solução Rápida

### 1. Acessar Vercel
- https://vercel.com/dashboard
- Selecione projeto: **pareto-case-nps**

### 2. Adicionar Variável
- Settings → Environment Variables
- **Key:** `TESS_DEFAULT_AGENT_ID`
- **Value:** `39004`
- **Environment:** Marque todas (Production, Preview, Development)
- Clique em **Save**

### 3. Redeploy
- Deployments → ⋮ → Redeploy
- ⚠️ Desmarque "Use existing Build Cache"
- Redeploy

## Pronto!
Após o deploy, teste no Telegram. O bot deve responder de forma inteligente.
