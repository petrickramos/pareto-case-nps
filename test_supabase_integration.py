
"""
Teste de Integração Supabase
Verifica se os agentes estão logando corretamente no Supabase
"""

import time
import json
from agents.sentiment_analyzer import SentimentAnalyzerAgent
from agents.message_generator import MessageGeneratorAgent
from agents.response_evaluator import ResponseEvaluatorAgent
from supabase_client import supabase_client

def run_test():
    print("🚀 INICIANDO TESTE DE INTEGRAÇÃO SUPABASE")
    print("=" * 70)
    
    # 1. Preparar Contexto Mock
    print("\n📦 1. Preparando Contexto Mock...")
    mock_contact_id = f"test_integration_{int(time.time())}"
    context = {
        "cliente": {
            "id": mock_contact_id,
            "nome": "Cliente Teste Integração",
            "email": "teste@integracao.com",
            "tempo_como_cliente": "1 ano"
        },
        "metricas": {
            "valor_total": 5000,
            "quantidade_deals": 1,
            "quantidade_tickets": 0,
            "riscos_identificados": 0
        },
        "riscos": [],
        "negocios": [{"nome": "Deal 1", "valor": 5000, "fase": "closedwon"}],
        "tickets": []
    }
    print(f"   ID do Cliente: {mock_contact_id}")
    
    # 2. Testar SentimentAnalyzerAgent
    print("\n🧠 2. Testando SentimentAnalyzerAgent...")
    analyzer = SentimentAnalyzerAgent()
    analysis = analyzer.analyze(context)
    print("   ✅ Análise concluída")
    
    # 3. Testar MessageGeneratorAgent
    print("\n✍️ 3. Testando MessageGeneratorAgent...")
    generator = MessageGeneratorAgent()
    message_result = generator.generate(context, analysis)
    print("   ✅ Mensagem gerada")
    
    # 4. Testar ResponseEvaluatorAgent
    print("\n📊 4. Testando ResponseEvaluatorAgent...")
    evaluator = ResponseEvaluatorAgent()
    # Simular resposta do cliente
    evaluator.evaluate(
        nps_score=9, 
        feedback_text="Adorei o teste de integração!", 
        context=context
    )
    print("   ✅ Avaliação concluída")
    
    # 5. Verificar no Supabase
    print("\n🔍 5. Verificando dados no Supabase...")
    time.sleep(2) # Dar um tempinho para a propagação se necessário
    
    # Verificar interações
    if supabase_client.client:
        interactions = supabase_client.client.table("nps_interactions") \
            .select("*") \
            .eq("contact_id", mock_contact_id) \
            .execute()
        
        print(f"\n   📋 Interações encontradas: {len(interactions.data)}")
        for interaction in interactions.data:
            print(f"      - [{interaction['interaction_type']}] {interaction['agent_name']} (Success: {interaction['success']})")
        
        # Verificar campanha
        campaigns = supabase_client.client.table("nps_campaigns") \
            .select("*") \
            .eq("contact_id", mock_contact_id) \
            .execute()
            
        print(f"\n   📋 Campanhas encontradas: {len(campaigns.data)}")
        if campaigns.data:
            camp = campaigns.data[0]
            print(f"      - Status: Mensagem Enviada={camp['message_sent']}, Resposta Date={camp['response_date']}")
            print(f"      - NPS: {camp['nps_score']} ({camp['nps_category']})")
            print(f"      - Sentimento Original: {camp['sentiment_score']}")
            
        if len(interactions.data) >= 3 and len(campaigns.data) >= 1:
            print("\n✅ SUCESSO: Todos os registros foram encontrados!")
        else:
            print("\n❌ FALHA: Faltam registros no banco.")
            
    else:
        print("\n❌ Erro: Cliente Supabase não inicializado.")

if __name__ == "__main__":
    run_test()
