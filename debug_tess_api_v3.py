
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

# Variação 4: Inteiro 0
payload_v4 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": 0,
    "max_tokens": 150,
    "stream": False
}

# Variação 5: Inteiro 1
payload_v5 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": 1,
    "max_tokens": 150,
    "stream": False
}

# Variação 6: Float 0.0
payload_v6 = {
    "messages": [{"role": "user", "content": "Olá"}],
    "tools": "no-tools",
    "temperature": 0.0,
    "stream": False
}

results = []
results.append(test_payload("V4 (Int 0)", payload_v4))
results.append(test_payload("V5 (Int 1)", payload_v5))
results.append(test_payload("V6 (Float 0.0)", payload_v6))

if any(results):
    print("\n✅ Encontramos o payload correto!")
else:
    print("\n❌ Ainda falhando.")
