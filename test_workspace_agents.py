"""
Script para testar os agentes Tess com IDs do workspace
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

TESS_API_KEY = os.getenv("TESS_API_KEY")
BASE_URL = "https://tess.pareto.io/api"

headers = {
    "Authorization": f"Bearer {TESS_API_KEY}",
    "Content-Type": "application/json"
}

# IDs dos agentes no workspace
AGENT_IDS = {
    "sentiment": "39004",  # [PETRICK] Agente de Análise de Sentimento
    "message": "39005"     # [PETRICK] Geração de Mensagens NPS
}

def test_agent(agent_id, agent_name):
    """Testa um agente específico"""
    print(f"\n{'='*60}")
    print(f"🧪 Testando: {agent_name}")
    print(f"   ID: {agent_id}")
    print(f"{'='*60}")
    
    # Testar endpoint OpenAI-compatible
    url = f"{BASE_URL}/agents/{agent_id}/openai/chat/completions"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente útil."
            },
            {
                "role": "user",
                "content": "Diga apenas 'Olá, estou funcionando!'"
            }
        ],
        "temperature": 0.5,
        "stream": False
    }
    
    try:
        print(f"\n📡 Chamando: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"   ✅ SUCESSO!")
                print(f"   📝 Resposta: {content}")
                return True
            else:
                print(f"   ⚠️ Resposta inesperada: {result}")
                return False
        else:
            print(f"   ❌ ERRO!")
            try:
                error = response.json()
                print(f"   📄 Detalhes: {error}")
            except:
                print(f"   📄 Texto: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 TESTE DE AGENTES TESS - IDs do Workspace")
    print("="*60)
    
    results = {}
    
    # Testar agente de sentimento
    results['sentiment'] = test_agent(
        AGENT_IDS['sentiment'],
        "[PETRICK] Agente de Análise de Sentimento"
    )
    
    # Testar agente de mensagem
    results['message'] = test_agent(
        AGENT_IDS['message'],
        "[PETRICK] Geração de Mensagens NPS"
    )
    
    # Resumo
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    print(f"Sentiment Agent (39004): {'✅ OK' if results['sentiment'] else '❌ FALHOU'}")
    print(f"Message Agent (39005):   {'✅ OK' if results['message'] else '❌ FALHOU'}")
    print(f"{'='*60}\n")
    
    if all(results.values()):
        print("🎉 TODOS OS AGENTES ESTÃO FUNCIONANDO!")
    else:
        print("⚠️ Alguns agentes falharam. Verifique os detalhes acima.")
