import requests
import os
from dotenv import load_dotenv

load_dotenv()

TESS_API_KEY = os.getenv("TESS_API_KEY")
BASE_URL = "https://tess.pareto.io"

headers = {
    "Authorization": f"Bearer {TESS_API_KEY}",
    "Content-Type": "application/json"
}

# Teste 1: Listar agentes disponíveis
print("Testando conexão com Tess AI...")
response = requests.get(f"{BASE_URL}/agents", headers=headers)

if response.status_code == 200:
    print("✅ Conexão OK!")
    agents = response.json()
    print(f"Agentes disponíveis: {len(agents.get('data', []))}")
    for agent in agents.get('data', [])[:5]:
        print(f"  - {agent.get('id')}: {agent.get('title', 'Sem título')}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
