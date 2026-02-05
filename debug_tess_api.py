
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TESS_API_KEY")
AGENT_ID = os.getenv("TESS_DEFAULT_AGENT_ID", "39004")
BASE_URL = "https://tess.pareto.io/api"

print(f"🔑 API Key: {API_KEY[:5]}...{API_KEY[-5:] if API_KEY else 'None'}")
print(f"🤖 Agent ID: {AGENT_ID}")

url = f"{BASE_URL}/agents/{AGENT_ID}/openai/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_payload(name, payload):
    print(f"\n🧪 Testando payload: {name}")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            print(f"Response: {response.text[:200]}...")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Payload 1: Como está no código atual (com tools="no-tools")
payload_atual = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "stream": False
}

# Payload 2: Formato OpenAI Padrão (conforme documentação)
payload_doc = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Olá"}],
    "temperature": 0.7,
    "max_tokens": 150,
    "stream": False
}

# Payload 3: Híbrido (sem tools, sem model)
payload_hibrido = {
    "messages": [{"role": "user", "content": "Olá"}],
    "temperature": 0.7,
    "max_tokens": 150,
    "stream": False
}

results = []
results.append(test_payload("Atual (com tools)", payload_atual))
results.append(test_payload("Doc (OpenAI Standard)", payload_doc))
results.append(test_payload("Híbrido", payload_hibrido))

if any(results):
    print("\n✅ Pelo menos um formato funcionou!")
else:
    print("\n❌ Todos falharam.")
