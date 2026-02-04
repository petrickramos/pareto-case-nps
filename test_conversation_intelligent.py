"""
Teste do Sistema de Conversação Inteligente
Simula conversa NPS completa usando ConversationManager
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from conversation_manager import conversation_manager


async def test_conversation_flow():
    """Testa fluxo completo de conversa"""
    
    print("="*60)
    print("🧪 TESTE: Conversação Inteligente NPS")
    print("="*60)
    
    test_chat_id = "test_12345"
    
    # Cenário 1: Detrator (score baixo)
    print("\n📍 Cenário 1: Cliente Detrator")
    print("-"*60)
    
    response1 = await conversation_manager.process_message(test_chat_id, "/start")
    print(f"Bot: {response1}\n")
    
    response2 = await conversation_manager.process_message(
        test_chat_id, 
        "Dou nota 3, o atendimento foi horrível e demorado"
    )
    print(f"Bot: {response2}\n")
    
    # Verificar sessão
    session = conversation_manager.get_session(test_chat_id)
    print(f"✅ Estado final: {session.state.value}")
    print(f"✅ Score NPS: {session.nps_score}/10")
    print(f"✅ Sentimento: {session.sentiment}")
    print(f"✅ Mensagens trocadas: {len(session.messages_history)}")
    
    # Cenário 2: Promotor (score alto)
    print("\n\n📍 Cenário 2: Cliente Promotor")
    print("-"*60)
    
    test_chat_id2 = "test_67890"
    
    response3 = await conversation_manager.process_message(test_chat_id2, "/start")
    print(f"Bot: {response3}\n")
    
    response4 = await conversation_manager.process_message(
        test_chat_id2,
        "10! Adorei tudo, a equipe é excelente!"
    )
    print(f"Bot: {response4}\n")
    
    session2 = conversation_manager.get_session(test_chat_id2)
    print(f"✅ Estado final: {session2.state.value}")
    print(f"✅ Score NPS: {session2.nps_score}/10")
    print(f"✅ Sentimento: {session2.sentiment}")
    
    # Cenário 3: Mensagem sem nota
    print("\n\n📍 Cenário 3: Mensagem sem nota (teste de inteligência)")
    print("-"*60)
    
    test_chat_id3 = "test_11111"
    
    response5 = await conversation_manager.process_message(test_chat_id3, "oi")
    print(f"Bot: {response5}\n")
    
    print("="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_conversation_flow())
