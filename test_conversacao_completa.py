#!/usr/bin/env python3
"""
Teste End-to-End - Conversação Completa com Personalização
Simula uma conversa completa do bot com cliente identificado e não identificado
"""

import sys
import os
from pathlib import Path
import asyncio

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from conversation_manager import ConversationManager

async def test_conversacao_cliente_identificado():
    """Teste 1: Conversa COM cliente identificado (Ana Silva)"""
    print("\n" + "="*70)
    print("TESTE 1: CONVERSAÇÃO COM CLIENTE IDENTIFICADO")
    print("="*70)
    
    manager = ConversationManager()
    chat_id = "test_123_identificado"
    username = "joao.silva@exemplo.com"  # Email que existe no HubSpot Mock
    
    print(f"\n📱 Chat ID: {chat_id}")
    print(f"👤 Username: {username}")
    
    # Mensagem 1: Saudação
    print("\n--- Mensagem 1: Primeira interação ---")
    print(f"Usuário: 'Oi'")
    response = await manager.process_message(chat_id, "Oi", username)
    print(f"Bot: {response}")
    
    # Verificar se cliente foi identificado
    session = manager.get_session(chat_id)
    if session.cliente_identificado:
        print(f"✅ Cliente identificado: {session.dados_cliente.get('properties', {}).get('firstname', 'N/A')}")
    else:
        print("⚠️ Cliente NÃO identificado")
    
    # Mensagem 2: Dar nota NPS
    print("\n--- Mensagem 2: Dar nota NPS ---")
    print(f"Usuário: 'Dou nota 9, adorei o atendimento!'")
    response = await manager.process_message(chat_id, "Dou nota 9, adorei o atendimento!", username)
    print(f"Bot: {response}")
    
    # Verificar estado
    print(f"\n📊 Estado final: {session.state.value}")
    print(f"📊 Score NPS: {session.nps_score}")
    print(f"📊 Sentimento: {session.sentiment}")
    
    return session.cliente_identificado

async def test_conversacao_cliente_nao_identificado():
    """Teste 2: Conversa SEM cliente identificado"""
    print("\n" + "="*70)
    print("TESTE 2: CONVERSAÇÃO SEM CLIENTE IDENTIFICADO")
    print("="*70)
    
    manager = ConversationManager()
    chat_id = "test_456_nao_identificado"
    username = "usuario_desconhecido"
    
    print(f"\n📱 Chat ID: {chat_id}")
    print(f"👤 Username: {username}")
    
    # Mensagem 1: Saudação
    print("\n--- Mensagem 1: Primeira interação ---")
    print(f"Usuário: 'Olá'")
    response = await manager.process_message(chat_id, "Olá", username)
    print(f"Bot: {response}")
    
    # Verificar se cliente foi identificado
    session = manager.get_session(chat_id)
    if session.cliente_identificado:
        print(f"✅ Cliente identificado: {session.dados_cliente.get('properties', {}).get('firstname', 'N/A')}")
    else:
        print("⚠️ Cliente NÃO identificado (esperado - usando fallback genérico)")
    
    # Mensagem 2: Dar nota NPS
    print("\n--- Mensagem 2: Dar nota NPS ---")
    print(f"Usuário: 'Nota 7, foi ok'")
    response = await manager.process_message(chat_id, "Nota 7, foi ok", username)
    print(f"Bot: {response}")
    
    # Verificar estado
    print(f"\n📊 Estado final: {session.state.value}")
    print(f"📊 Score NPS: {session.nps_score}")
    print(f"📊 Sentimento: {session.sentiment}")
    
    return not session.cliente_identificado

async def test_conversacao_off_script():
    """Teste 3: Mensagem off-script com personalização"""
    print("\n" + "="*70)
    print("TESTE 3: MENSAGEM OFF-SCRIPT COM PERSONALIZAÇÃO")
    print("="*70)
    
    manager = ConversationManager()
    chat_id = "test_789_offscript"
    username = "joao.silva@exemplo.com"
    
    print(f"\n📱 Chat ID: {chat_id}")
    print(f"👤 Username: {username}")
    
    # Mensagem off-script
    print("\n--- Mensagem off-script ---")
    print(f"Usuário: 'Como assim avaliar?'")
    response = await manager.process_message(chat_id, "Como assim avaliar?", username)
    print(f"Bot: {response}")
    
    # Verificar se usou nome na resposta
    session = manager.get_session(chat_id)
    if session.cliente_identificado:
        nome = session.dados_cliente.get('properties', {}).get('firstname', '')
        if nome and nome.lower() in response.lower():
            print(f"✅ Resposta personalizada com nome '{nome}'")
            return True
        else:
            print(f"⚠️ Resposta sem personalização (nome não encontrado)")
            return False
    else:
        print("⚠️ Cliente não identificado")
        return False

async def main():
    """Executar todos os testes"""
    print("\n" + "🧪 " + "="*68)
    print("   TESTE END-TO-END - CONVERSAÇÃO COMPLETA COM PERSONALIZAÇÃO")
    print("="*70)
    
    # Verificar HubSpot Mock
    print("\n🔍 Verificando HubSpot Mock...")
    import requests
    try:
        response = requests.get("http://localhost:4010/__admin/mappings", timeout=3)
        if response.status_code == 200:
            print("✅ HubSpot Mock está ONLINE")
        else:
            print(f"⚠️ HubSpot Mock retornou status {response.status_code}")
            print("   Testes vão usar fallback genérico")
    except:
        print("⚠️ HubSpot Mock NÃO está rodando")
        print("   Testes vão usar fallback genérico")
    
    # Executar testes
    resultados = []
    
    try:
        resultado1 = await test_conversacao_cliente_identificado()
        resultados.append(("Cliente Identificado", resultado1))
    except Exception as e:
        print(f"\n❌ Erro no Teste 1: {e}")
        resultados.append(("Cliente Identificado", False))
    
    try:
        resultado2 = await test_conversacao_cliente_nao_identificado()
        resultados.append(("Cliente Não Identificado", resultado2))
    except Exception as e:
        print(f"\n❌ Erro no Teste 2: {e}")
        resultados.append(("Cliente Não Identificado", False))
    
    try:
        resultado3 = await test_conversacao_off_script()
        resultados.append(("Off-Script Personalizado", resultado3))
    except Exception as e:
        print(f"\n❌ Erro no Teste 3: {e}")
        resultados.append(("Off-Script Personalizado", False))
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")
    
    total = len(resultados)
    passou = sum(1 for _, r in resultados if r)
    
    print(f"\n📊 Total: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Bot pronto para deploy!")
        return 0
    else:
        print("\n⚠️ Alguns testes falharam")
        print("   Revisar implementação antes do deploy")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
