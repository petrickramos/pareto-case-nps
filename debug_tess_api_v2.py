
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TESS_API_KEY")
AGENT_ID = os.getenv("TESS_DEFAULT_AGENT_ID", "39004")
BASE_URL = "https://tess.pareto.io/api"

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

# Variação 1: Tudo junto (tools + temperature + max_tokens)
payload_v1 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": 0.7,
    "max_tokens": 150,
    "stream": False
}

# Variação 2: Temperature como string (já vi APIs assim)
payload_v2 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": "0.7",
    "max_tokens": 150,
    "stream": False
}

# Variação 3: Sem max_tokens, só temperature
payload_v3 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": 0.7,
    "stream": False
}

results = []
results.append(test_payload("V1 (Completo)", payload_v1))
results.append(test_payload("V2 (Temp String)", payload_v2))
results.append(test_payload("V3 (Sem max_tokens)", payload_v3))

if any(results):
    print("\n✅ Encontramos o payload correto!")
else:
    print("\n❌ Ainda falhando.")
