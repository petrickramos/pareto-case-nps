import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TessClient:
    def __init__(self):
        self.api_key = os.getenv("TESS_API_KEY")
        self.base_url = "https://tess.pareto.io/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def list_agents(self, limit=50):
        """Lista todos os agentes disponíveis na Tess AI"""
        url = f"{self.base_url}/agents"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar agentes: {e}")
            return None
    
    def get_agent(self, agent_id):
        """Obtém detalhes de um agente específico"""
        url = f"{self.base_url}/agents/{agent_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter agente {agent_id}: {e}")
            return None
    
    def execute_agent(self, agent_id, input_data):
        """Executa um agente com dados de entrada"""
        url = f"{self.base_url}/agents/{agent_id}/execute"
        
        try:
            response = requests.post(url, headers=self.headers, json=input_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao executar agente {agent_id}: {e}")
            return None


if __name__ == "__main__":
    print("🤖 Testando conexão com Tess AI...")
    print("=" * 50)
    
    client = TessClient()
    
    # Testar listagem de agentes
    print("\n📋 Listando agentes disponíveis:")
    agents = client.list_agents(limit=5)
    
    if agents:
        print(f"✅ Conexão OK! Encontrados {len(agents.get('data', []))} agentes\n")
        
        for i, agent in enumerate(agents.get('data', [])[:5], 1):
            print(f"{i}. {agent.get('title', 'Sem título')}")
            print(f"   ID: {agent.get('id')}")
            print(f"   Descrição: {agent.get('description', 'N/A')[:80]}...")
            print()
    else:
        print("❌ Falha ao conectar com a API da Tess")
