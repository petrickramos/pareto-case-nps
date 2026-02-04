"""
Teste simples e direto da API Tess
Usando endpoint correto /agents/{id}/execute
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

# Usar agente público para teste (ID 45 - Anúncios Google Ads)
AGENT_ID = "45"

print("\n" + "="*60)
print("🧪 TESTE DIRETO DA API TESS")
print("="*60)

print(f"\n📡 Endpoint: {BASE_URL}/agents/{AGENT_ID}/execute")
print(f"🔑 Token configurado: {'✅ Sim' if TESS_API_KEY else '❌ Não'}")

payload = {
    "input": "Crie uma saudação amigável e profissional",
    "wait_execution": True
}

print(f"\n📤 Enviando requisição...")
print(f"   Payload: {payload}")

try:
    response = requests.post(
        f"{BASE_URL}/agents/{AGENT_ID}/execute",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\n📥 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCESSO!")
        print(f"\n📄 Resposta completa:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Extrair output
        output = result.get('output', '')
        if output:
            print(f"\n💬 Output extraído:")
            print(f"   {output}")
    else:
        print(f"❌ ERRO!")
        try:
            error = response.json()
            print(f"📄 Detalhes: {error}")
        except:
            print(f"📄 Texto: {response.text}")
            
except Exception as e:
    print(f"❌ EXCEÇÃO: {e}")

print("\n" + "="*60 + "\n")
