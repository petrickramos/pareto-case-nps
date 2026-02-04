"""
Script para explorar diferentes endpoints da API Tess
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

def test_endpoint(method, endpoint, payload=None, description=""):
    """Testa um endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"   {method} {url}")
    print(f"{'='*70}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCESSO!")
            # Mostrar primeiras linhas do resultado
            result_str = json.dumps(result, indent=2)
            lines = result_str.split('\n')
            print("   📄 Resposta (primeiras 20 linhas):")
            for i, line in enumerate(lines[:20]):
                print(f"      {line}")
            if len(lines) > 20:
                print(f"      ... ({len(lines) - 20} linhas restantes)")
            return result
        else:
            print(f"   ❌ Erro {response.status_code}")
            try:
                error = response.json()
                print(f"   📄 Detalhes: {error}")
            except:
                print(f"   📄 Texto: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 EXPLORANDO API TESS - Diferentes Endpoints")
    print("="*70)
    
    # 1. Listar agentes
    agents = test_endpoint(
        "GET",
        "/agents?limit=100",
        description="Listar todos os agentes"
    )
    
    # 2. Tentar endpoint com workspace_id
    test_endpoint(
        "GET",
        "/agents?workspace_id=1270376",
        description="Listar agentes do workspace 1270376"
    )
    
    # 3. Tentar acessar agente por ID do workspace
    test_endpoint(
        "GET",
        "/agents/39004",
        description="Obter agente 39004 (ID do workspace)"
    )
    
    # 4. Tentar endpoint de templates
    test_endpoint(
        "GET",
        "/templates",
        description="Listar templates"
    )
    
    # 5. Tentar endpoint de templates com ID
    test_endpoint(
        "GET",
        "/templates/39004",
        description="Obter template 39004"
    )
    
    # 6. Se conseguimos listar agentes, procurar pelos nossos
    if agents and 'data' in agents:
        print(f"\n{'='*70}")
        print("🔍 PROCURANDO AGENTES PETRICK")
        print(f"{'='*70}")
        
        found = []
        for agent in agents['data']:
            name = agent.get('name', '')
            if 'PETRICK' in name.upper() or 'petrick' in name.lower():
                found.append(agent)
                print(f"\n   ✅ Encontrado: {name}")
                print(f"      ID: {agent.get('id')}")
                print(f"      Slug: {agent.get('slug')}")
                print(f"      Public: {agent.get('is_public')}")
        
        if not found:
            print("\n   ⚠️ Nenhum agente PETRICK encontrado na listagem")
            print("   💡 Isso pode significar que os agentes são privados do workspace")
    
    print(f"\n{'='*70}\n")
