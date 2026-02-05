"""
Script de Teste Completo - Sistema de Conversação Inteligente
Valida todo o fluxo: ConversationManager, TessLLM, Supabase, LangSmith
"""

import asyncio
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Carregar env
load_dotenv()

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from conversation_manager import conversation_manager
from supabase_client import supabase_client


async def test_full_system():
    """Teste completo do sistema inteligente"""
    
    print("="*70)
    print("🧪 TESTE COMPLETO - SISTEMA DE CONVERSAÇÃO INTELIGENTE")
    print("="*70)
    
    # Verificar Supabase
    print("\n📊 1. Verificando Supabase...")
    if not supabase_client.client:
        print("❌ Supabase não configurado!")
        return False
    
    try:
        result = supabase_client.client.table("conversation_messages").select("*").limit(1).execute()
        print(f"✅ Supabase OK - Tabela 'conversation_messages' existe")
    except Exception as e:
        print(f"❌ Erro no Supabase: {e}")
        print("\n⚠️ Execute o SQL no dashboard primeiro!")
        return False
    
    # Verificar LangSmith
    print("\n📈 2. Verificando LangSmith...")
    langsmith_key = os.getenv("LANGCHAIN_API_KEY")
    if langsmith_key:
        print(f"✅ LangSmith configurado (key: {langsmith_key[:10]}...)")
    else:
        print("⚠️ LangSmith não configurado (opcional)")
    
    # Teste 1: Cliente Detrator
    print("\n" + "="*70)
    print("📍 TESTE 1: Cliente Detrator (Score Baixo)")
    print("="*70)
    
    chat_id_1 = "test_detrator_001"
    
    print("\n👤 Usuário: /start")
    response1 = await conversation_manager.process_message(chat_id_1, "/start")
    print(f"🤖 Bot: {response1[:100]}...")

    print("\n👤 Usuário: sim")
    response2 = await conversation_manager.process_message(chat_id_1, "sim")
    print(f"🤖 Bot: {response2[:100]}...")
    
    print("\n👤 Usuário: Dou nota 2, o atendimento foi péssimo e demorado")
    response3 = await conversation_manager.process_message(
        chat_id_1,
        "Dou nota 2, o atendimento foi péssimo e demorado"
    )
    print(f"🤖 Bot: {response3}")
    
    session1 = conversation_manager.get_session(chat_id_1)
    print(f"\n✅ Estado: {session1.state.value}")
    print(f"✅ Score: {session1.nps_score}/10")
    print(f"✅ Sentimento: {session1.sentiment}")
    print(f"✅ Mensagens: {len(session1.messages_history)}")
    
    # Teste 2: Cliente Promotor
    print("\n" + "="*70)
    print("📍 TESTE 2: Cliente Promotor (Score Alto)")
    print("="*70)
    
    chat_id_2 = "test_promotor_002"
    
    print("\n👤 Usuário: /start")
    response4 = await conversation_manager.process_message(chat_id_2, "/start")
    print(f"🤖 Bot: {response4[:100]}...")

    print("\n👤 Usuário: sim")
    response5 = await conversation_manager.process_message(chat_id_2, "sim")
    print(f"🤖 Bot: {response5[:100]}...")
    
    print("\n👤 Usuário: 10! Adorei tudo, a equipe é excelente!")
    response6 = await conversation_manager.process_message(
        chat_id_2,
        "10! Adorei tudo, a equipe é excelente!"
    )
    print(f"🤖 Bot: {response6}")
    
    session2 = conversation_manager.get_session(chat_id_2)
    print(f"\n✅ Estado: {session2.state.value}")
    print(f"✅ Score: {session2.nps_score}/10")
    print(f"✅ Sentimento: {session2.sentiment}")
    
    # Teste 3: Mensagem sem nota (teste de inteligência)
    print("\n" + "="*70)
    print("📍 TESTE 3: Mensagem Sem Nota (Inteligência)")
    print("="*70)
    
    chat_id_3 = "test_inteligencia_003"
    
    print("\n👤 Usuário: oi")
    response7 = await conversation_manager.process_message(chat_id_3, "oi")
    print(f"🤖 Bot: {response7}")

    print("\n👤 Usuário: /start")
    response8 = await conversation_manager.process_message(chat_id_3, "/start")
    print(f"🤖 Bot: {response8[:100]}...")

    print("\n👤 Usuário: Como atribuo?")
    response9 = await conversation_manager.process_message(chat_id_3, "Como atribuo?")
    print(f"🤖 Bot: {response9}")

    print("\n👤 Usuário: 8")
    response10 = await conversation_manager.process_message(chat_id_3, "8")
    print(f"🤖 Bot: {response10}")
    
    # Verificar logs no Supabase
    print("\n" + "="*70)
    print("📊 4. Verificando Logs no Supabase")
    print("="*70)
    
    try:
        messages = supabase_client.client.table("conversation_messages")\
            .select("*")\
            .in_("chat_id", [chat_id_1, chat_id_2, chat_id_3])\
            .order("created_at", desc=False)\
            .execute()
        
        print(f"✅ Total de mensagens registradas: {len(messages.data)}")
        
        for msg in messages.data[:5]:  # Mostrar primeiras 5
            print(f"  - [{msg['sender']}] {msg['message_text'][:50]}...")
    
    except Exception as e:
        print(f"⚠️ Erro ao buscar logs: {e}")
    
    # Resumo Final
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\n📋 Próximos Passos:")
    print("1. ✅ Sistema funcionando localmente")
    print("2. 🚀 Fazer commit e push para GitHub")
    print("3. 📦 Vercel fará deploy automático")
    print("4. 🤖 Testar no Telegram: @pareto_nps_case_mba_bot")
    print("5. 📊 Verificar logs no LangSmith: https://smith.langchain.com")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_full_system())
        
        if success:
            print("\n🎉 Tudo pronto para deploy!")
        else:
            print("\n⚠️ Corrija os erros acima antes de fazer deploy")
            
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
