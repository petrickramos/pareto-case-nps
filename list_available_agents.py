"""
Lista os primeiros agentes disponíveis na API Tess
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
print("📋 AGENTES DISPONÍVEIS NA API TESS")
print("="*70)

response = requests.get(f"{BASE_URL}/agents?limit=10", headers=headers)

if response.status_code == 200:
    result = response.json()
    agents = result.get('data', [])
    
    print(f"\n✅ Encontrados {len(agents)} agentes (mostrando primeiros 10):\n")
    
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.get('title', 'Sem título')}")
        print(f"   ID: {agent.get('id')}")
        print(f"   Slug: {agent.get('slug', 'N/A')}")
        print(f"   Workspace: {agent.get('workspace_id')}")
        print(f"   Visibilidade: {agent.get('visibility')}")
        print(f"   Tipo: {agent.get('type')}")
        
        # Mostrar campos obrigatórios se houver
        questions = agent.get('questions', [])
        if questions:
            required = [q.get('name') for q in questions if q.get('required')]
            if required:
                print(f"   Campos obrigatórios: {', '.join(required[:3])}")
        print()
    
    # Procurar agente mais simples (menos campos obrigatórios)
    print("\n" + "="*70)
    print("🔍 PROCURANDO AGENTE MAIS SIMPLES (menos campos obrigatórios)")
    print("="*70 + "\n")
    
    simplest = None
    min_fields = float('inf')
    
    for agent in agents:
        questions = agent.get('questions', [])
        required_count = sum(1 for q in questions if q.get('required'))
        
        if required_count < min_fields:
            min_fields = required_count
            simplest = agent
    
    if simplest:
        print(f"✅ Agente mais simples encontrado:")
        print(f"   Nome: {simplest.get('title')}")
        print(f"   ID: {simplest.get('id')}")
        print(f"   Campos obrigatórios: {min_fields}")
        print(f"\n   💡 Use este ID no código: TESS_DEFAULT_AGENT_ID={simplest.get('id')}")
    
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)

print("\n" + "="*70 + "\n")
