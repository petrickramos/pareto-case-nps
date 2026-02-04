"""
Testa agentes PETRICK com payload correto (incluindo tools)
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

print("\n" + "="*70)
print("🧪 TESTE FINAL - AGENTES PETRICK COM PAYLOAD CORRETO")
print("="*70)

# Teste 1: Agente de Sentimento (39004)
print(f"\n{'='*70}")
print("🤖 Agente de Análise de Sentimento (39004)")
print(f"{'='*70}")

payload_sentiment = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "Você é um analista de Customer Success especializado em NPS."
        },
        {
            "role": "user",
            "content": "Analise o sentimento: Cliente disse 'Estou muito satisfeito com o atendimento!'"
        }
    ],
    "temperature": 0.2,
    "max_tokens": 300,
    "stream": False,
    "tools": []  # Campo obrigatório (vazio se não usar tools)
}

try:
    response = requests.post(
        f"{BASE_URL}/agents/39004/openai/chat/completions",
        headers=headers,
        json=payload_sentiment,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"✅ SUCESSO!")
        print(f"\n📝 Resposta do agente:")
        print(f"{content}\n")
    else:
        print(f"❌ Erro: {response.text}")
except Exception as e:
    print(f"❌ Exceção: {e}")

# Teste 2: Agente de Mensagens (39005)
print(f"\n{'='*70}")
print("🤖 Geração de Mensagens NPS (39005)")
print(f"{'='*70}")

payload_message = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "Você é um especialista em copywriting para NPS."
        },
        {
            "role": "user",
            "content": "Crie uma mensagem de NPS empática para um cliente promotor chamado João."
        }
    ],
    "temperature": 0.7,
    "max_tokens": 300,
    "stream": False,
    "tools": []
}

try:
    response = requests.post(
        f"{BASE_URL}/agents/39005/openai/chat/completions",
        headers=headers,
        json=payload_message,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"✅ SUCESSO!")
        print(f"\n📝 Resposta do agente:")
        print(f"{content}\n")
    else:
        print(f"❌ Erro: {response.text}")
except Exception as e:
    print(f"❌ Exceção: {e}")

print("="*70)
print("✅ TESTES CONCLUÍDOS")
print("="*70 + "\n")
