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

## Passo 3: Atualizar N8N

1. Acesse seu workflow N8N
2. Encontre o nó **HTTP Request** que chama `/nps/evaluate`
3. Atualize a URL:
   - **Antes:** `https://pareto-nps.railway.app/nps/evaluate`
   - **Depois:** `https://SEU-PROJETO.vercel.app/nps/evaluate`

4. Salve e publique o workflow

## Passo 4: Testar

1. Envie uma mensagem para o bot do Telegram
2. Responda com uma nota (ex: `8`)
3. Verifique se recebeu a resposta empática
4. Confira no Supabase se o registro foi salvo:
   ```sql
   SELECT * FROM nps_respostas ORDER BY created_at DESC LIMIT 5;
   ```

## ✅ Checklist

- [ ] Supabase criado e schema executado
- [ ] Connection String copiada
- [ ] Código no GitHub
- [ ] Deploy no Vercel concluído
- [ ] Variáveis de ambiente configuradas
- [ ] N8N atualizado com nova URL
- [ ] Teste realizado com sucesso

## 🆘 Troubleshooting

### Erro: "Module not found"
- Verifique se `requirements.txt` está completo
- Rode: `vercel --prod` novamente

### Erro: "Database connection failed"
- Verifique se a Connection String está correta
- Certifique-se de substituir `[YOUR-PASSWORD]`

### Erro: "Function timeout"
- Vercel tem limite de 10s para Hobby Plan
- Se necessário, otimize chamadas LLM

## 💰 Custos

- **Supabase:** GRÁTIS (500MB, 50.000 requisições/mês)
- **Vercel:** GRÁTIS (100GB bandwidth, ilimitado para hobby)
- **N8N Cloud:** GRÁTIS (5.000 execuções/mês)

**Total: R$ 0,00/mês** 🎉
