"""
Teste simples e rápido do Supabase
"""

import os
from dotenv import load_dotenv

print("1. Carregando .env...")
load_dotenv()

print("2. Verificando variáveis...")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"   URL: {url[:30]}..." if url else "   URL: ❌ Não encontrada")
print(f"   KEY: {key[:30]}..." if key else "   KEY: ❌ Não encontrada")

if not url or not key:
    print("\n❌ Variáveis não configuradas!")
    exit(1)

print("\n3. Importando Supabase...")
try:
    from supabase import create_client, Client
    print("   ✅ Import OK")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

print("\n4. Conectando...")
try:
    client = create_client(url, key)
    print("   ✅ Cliente criado")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

print("\n5. Testando inserção...")
try:
    result = client.table("nps_interactions").insert({
        "contact_id": "teste_rapido",
        "interaction_type": "test",
        "agent_name": "TestScript",
        "input_data": {"teste": True},
        "output_data": {"resultado": "ok"},
        "success": True,
        "processing_time_ms": 10
    }).execute()
    
    if result.data:
        print(f"   ✅ Dados inseridos! ID: {result.data[0]['id']}")
    else:
        print(f"   ⚠️ Resultado vazio: {result}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

print("\n🎉 TUDO FUNCIONANDO!")
