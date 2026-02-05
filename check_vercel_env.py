#!/usr/bin/env python3
"""
Script para verificar variáveis de ambiente necessárias
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE\n")
print("="*60)

required_vars = {
    "TESS_API_KEY": "Chave da API Tess",
    "TESS_DEFAULT_AGENT_ID": "ID do agente padrão",
    "TELEGRAM_BOT_TOKEN": "Token do bot Telegram",
    "SUPABASE_URL": "URL do Supabase",
    "SUPABASE_ANON_KEY": "Chave anônima do Supabase",
    "LANGCHAIN_API_KEY": "Chave da API LangChain"
}

missing = []
present = []

for var, desc in required_vars.items():
    value = os.getenv(var)
    if value:
        # Mostrar apenas início e fim para segurança
        masked = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else "***"
        present.append((var, desc, masked))
        print(f"✅ {var}: {masked}")
    else:
        missing.append((var, desc))
        print(f"❌ {var}: NÃO CONFIGURADA")

print("\n" + "="*60)
print(f"\n📊 Resumo: {len(present)}/{len(required_vars)} variáveis configuradas")

if missing:
    print("\n⚠️ VARIÁVEIS FALTANDO:")
    for var, desc in missing:
        print(f"   - {var}: {desc}")
    print("\n💡 Configure essas variáveis na Vercel:")
    print("   1. Acesse: https://vercel.com/dashboard")
    print("   2. Selecione o projeto")
    print("   3. Settings → Environment Variables")
    print("   4. Adicione as variáveis faltantes")
    print("   5. Redeploy")
else:
    print("\n🎉 Todas as variáveis estão configuradas!")

# Testar conexão com Tess
print("\n" + "="*60)
print("🧪 TESTANDO CONEXÃO COM TESS AI\n")

if os.getenv("TESS_API_KEY") and os.getenv("TESS_DEFAULT_AGENT_ID"):
    import requests
    
    api_key = os.getenv("TESS_API_KEY")
    agent_id = os.getenv("TESS_DEFAULT_AGENT_ID")
    url = f"https://tess.pareto.io/api/agents/{agent_id}/openai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": "teste"}],
        "tools": "no-tools",
        "temperature": 1,
        "max_tokens": 50,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Conexão com Tess AI: OK")
            print(f"   Resposta recebida com sucesso")
        else:
            print(f"❌ Erro {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
else:
    print("⚠️ Não é possível testar sem TESS_API_KEY e TESS_DEFAULT_AGENT_ID")

print("\n" + "="*60)
