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
    
    
    def generate(self, prompt, max_tokens=300, temperature=0.7, agent_id=None, system_prompt=None):
        """
        Gera texto usando a API da Tess AI
        Método compatível com LangChain TessLLM wrapper
        
        Usa o endpoint OpenAI-compatible com formato correto para agentes workspace:
        https://docs.tess.im/api/endpoints/agents/execute_openai_compatible/
        
        Args:
            prompt: Texto de entrada para geração
            max_tokens: Número máximo de tokens na resposta (não usado no formato atual)
            temperature: Temperatura para geração (0.0 a 1.0) (não usado no formato atual)
            agent_id: ID do agente a usar (opcional, usa agente padrão se não especificado)
            system_prompt: Prompt do sistema (opcional)
            
        Returns:
            Texto gerado pela API
        """
        # Usar agente padrão se não especificado
        if not agent_id:
            agent_id = os.getenv("TESS_DEFAULT_AGENT_ID", "39004")  # Agente de sentimento
        
        # Usar endpoint OpenAI-compatible
        url = f"{self.base_url}/agents/{agent_id}/openai/chat/completions"
        
        # Montar mensagens
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Payload correto para agentes workspace Tess
        payload = {
            "messages": messages,
            "tools": "no-tools",  # STRING obrigatória: 'no-tools', 'internet', 'deep_analysis', etc.
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extrair texto da resposta (formato OpenAI)
            # Resposta contém: choices[0].message.content
            if isinstance(result, dict) and 'choices' in result:
                if len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    if content:
                        return str(content).strip()
            
            # Fallback se não conseguir extrair content
            return str(result)
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao gerar texto com Tess AI: {e}")
            # Fallback: retornar mensagem padrão
            return f"Olá! Como posso ajudar você hoje?"


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
