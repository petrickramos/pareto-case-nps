"""
Testa os agentes PETRICK recém-publicados
IDs: 39004 (Sentiment) e 39005 (Message)
"""

import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

TESS_API_KEY = os.getenv("TESS_API_KEY")
BASE_URL = "https://tess.pareto.io/api"

headers = {
    "Authorization": f"Bearer {TESS_API_KEY}",
    "Content-Type": "application/json"
}

AGENTS = {
    "39004": "Agente de Análise de Sentimento",
    "39005": "Geração de Mensagens NPS"
}

print("\n" + "="*70)
print("🧪 TESTANDO AGENTES PETRICK PUBLICADOS")
print("="*70)

for agent_id, name in AGENTS.items():
    print(f"\n{'='*70}")
    print(f"🤖 Testando: {name} (ID: {agent_id})")
    print(f"{'='*70}")
    
    # 1. Testar GET /agents/{id}
    print(f"\n1️⃣ GET /agents/{agent_id}")
    try:
        response = requests.get(f"{BASE_URL}/agents/{agent_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            agent = response.json()
            print(f"   ✅ Agente encontrado!")
            print(f"   Nome: {agent.get('title')}")
            print(f"   Slug: {agent.get('slug')}")
            print(f"   Visibilidade: {agent.get('visibility')}")
        else:
            print(f"   ❌ Erro: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # 2. Testar OpenAI endpoint
    print(f"\n2️⃣ POST /agents/{agent_id}/openai/chat/completions")
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Teste simples: diga olá"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/agents/{agent_id}/openai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"   ✅ SUCESSO!")
                print(f"   📝 Resposta: {content[:200]}")
            else:
                print(f"   ⚠️ Resposta inesperada: {json.dumps(result, indent=2)[:200]}")
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

print("\n" + "="*70)
print("✅ TESTES CONCLUÍDOS")
print("="*70 + "\n")
