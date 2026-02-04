# 🚀 Deploy no Vercel + Supabase (100% GRÁTIS)

## Passo 1: Configurar Supabase (Postgres)

1. Acesse: https://supabase.com
2. Crie uma conta (grátis, sem cartão)
3. Crie um novo projeto:
   - Nome: `pareto-nps`
   - Região: `South America (São Paulo)`
   - Database Password: (anote essa senha!)

4. Aguarde ~2 minutos para o projeto ser criado

5. Vá em **SQL Editor** e execute o arquivo `supabase_schema.sql`:
   ```sql
   -- Cole o conteúdo de supabase_schema.sql aqui
   ```

6. Copie as chaves API:
   - Vá em **Project Settings** → **API**
   - Copie a **URL** (`SUPABASE_URL`)
   - Copie a chave **anon public** (`SUPABASE_KEY`)

## Passo 2: Deploy no Vercel

### Opção A: Via GitHub (Recomendado)

1. Certifique-se que o código está no GitHub (já está!)

2. Acesse: https://vercel.com/new
3. Importe o repositório `pareto-case-nps`
4. Configure as variáveis de ambiente:
   - `SUPABASE_URL`: Cole a URL do projeto
   - `SUPABASE_KEY`: Cole a chave anon public
   - `TESS_API_KEY`: Sua chave da Tess AI
   - `HUBSPOT_API_URL`: Use `http://localhost:4010` (Nota: em produção real, precisaria de um mock público)
   - `HUBSPOT_API_KEY`: `pat-na1-123`

5. Clique em **Deploy**

6. Aguarde ~2 minutos

7. Copie a URL do deploy (ex: `https://pareto-nps.vercel.app`)

### Opção B: Via Vercel CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer login
vercel login

# Deploy
cd pareto-case/langchain
vercel

# Adicionar variáveis de ambiente
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
vercel env add TESS_API_KEY

# Deploy em produção
vercel --prod
```

## Passo 3: Configurar Webhook do Telegram (CRÍTICO!)

Para que o bot funcione, você precisa "avisar" ao Telegram para enviar as mensagens para seu deploy na Vercel.

1.  Pegue sua URL da Vercel (ex: `https://pareto-nps.vercel.app`)
2.  Substitua na URL abaixo junto com seu Token do Bot:

```
https://api.telegram.org/bot7266298448:AAGqX38TT6A1643cZO07zbiEFQB6x21nlQ4/setWebhook?url=https://[SUA-APP].vercel.app/telegram/webhook&secret_token=pareto-secret-123
```

3.  Cole essa URL no seu navegador e dê Enter.
4.  Você deve ver: `{"ok":true, "result":true, "description":"Webhook was set"}`.

## Passo 4: Configurar LangSmith (Auditoria)
Adicione as variáveis na Vercel para ativar o rastreamento:
- `LANGCHAIN_TRACING_V2`: `true`
- `LANGCHAIN_ENDPOINT`: `https://api.smith.langchain.com`
- `LANGCHAIN_API_KEY`: (Cole sua chave lsv2_... aqui)
- `LANGCHAIN_PROJECT`: `pareto-nps-case`
- `TELEGRAM_BOT_TOKEN`: `7266298448:AAGqX38TT6A1643cZO07zbiEFQB6x21nlQ4`
- `TELEGRAM_WEBHOOK_SECRET`: `pareto-secret-123`

## Passo 5: Testar
1. Abra o bot no Telegram: `t.me/pareto_nps_case_mba_bot`
2. Envie `/start` e veja se ele responde!


## ✅ Checklist
- [ ] Supabase configurado
- [ ] Código no GitHub
- [ ] Deploy Vercel (com novas variáveis)
- [ ] Webhook Telegram Configurado
- [ ] LangSmith Configurado
- [ ] Bot respondendo no Telegram!

## 💰 Custos
- **Supabase:** GRÁTIS
- **Vercel:** GRÁTIS
- **LangSmith:** GRÁTIS (plano Developer)
- **Telegram:** GRÁTIS

**Total: R$ 0,00/mês** 🎉
