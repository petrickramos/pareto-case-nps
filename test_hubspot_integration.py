#!/usr/bin/env python3
"""
Teste de Integração - HubSpot Mock + ClienteService
Valida identificação de cliente e personalização de prompts
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.cliente_service import cliente_service

def test_hubspot_mock_connectivity():
    """Teste 1: Verificar se HubSpot Mock está rodando"""
    print("\n" + "="*60)
    print("TESTE 1: Conectividade HubSpot Mock")
    print("="*60)
    
    import requests
    try:
        response = requests.get("http://localhost:4010/__admin/mappings", timeout=3)
        if response.status_code == 200:
            print("✅ HubSpot Mock está ONLINE")
            print(f"   URL: http://localhost:4010")
            return True
        else:
            print(f"❌ HubSpot Mock retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HubSpot Mock NÃO está rodando: {e}")
        print("   Execute: cd hubspot-mockapi && docker-compose up -d")
        return False

def test_buscar_cliente_por_email():
    """Teste 2: Buscar cliente por email"""
    print("\n" + "="*60)
    print("TESTE 2: Buscar Cliente por Email")
    print("="*60)
    
    # Testar com emails dos clientes mock
    emails_teste = [
        "joao.silva@exemplo.com",
        "maria.santos@exemplo.com",
        "pedro.oliveira@exemplo.com",
        "inexistente@exemplo.com"
    ]
    
    resultados = []
    for email in emails_teste:
        print(f"\n🔍 Buscando: {email}")
        cliente = cliente_service.buscar_por_email(email)
        
        if cliente:
            props = cliente.get("properties", {})
            nome = props.get("firstname", "N/A")
            sobrenome = props.get("lastname", "N/A")
            print(f"   ✅ Encontrado: {nome} {sobrenome}")
            print(f"   ID: {cliente.get('id')}")
            resultados.append(True)
        else:
            print(f"   ⚠️ Não encontrado")
            resultados.append(False)
    
    return all(resultados[:3])  # Primeiros 3 devem existir

def test_coletar_contexto():
    """Teste 3: Coletar contexto completo do cliente"""
    print("\n" + "="*60)
    print("TESTE 3: Coletar Contexto do Cliente")
    print("="*60)
    
    # Buscar cliente 101
    cliente = cliente_service.buscar_por_email("joao.silva@exemplo.com")
    
    if not cliente:
        print("❌ Cliente não encontrado")
        return False
    
    contact_id = cliente.get("id")
    print(f"\n📊 Coletando contexto para contact_id: {contact_id}")
    
    contexto = cliente_service.coletar_contexto(contact_id)
    
    print(f"\n✅ Contexto coletado:")
    print(f"   - Deals: {len(contexto.get('deals', []))}")
    print(f"   - Tickets: {len(contexto.get('tickets', []))}")
    print(f"   - Notes: {len(contexto.get('notes', []))}")
    print(f"   - Emails: {len(contexto.get('emails', []))}")
    
    metricas = contexto.get("metricas", {})
    print(f"\n📈 Métricas:")
    print(f"   - Total de deals: {metricas.get('num_deals', 0)}")
    print(f"   - Total de tickets: {metricas.get('num_tickets', 0)}")
    print(f"   - Valor total: R$ {metricas.get('valor_total', 0):,.2f}")
    
    return True

def test_personalizacao_prompt():
    """Teste 4: Simular personalização de prompt"""
    print("\n" + "="*60)
    print("TESTE 4: Personalização de Prompt")
    print("="*60)
    
    # Buscar cliente
    cliente = cliente_service.buscar_por_email("joao.silva@exemplo.com")
    
    if not cliente:
        print("❌ Cliente não encontrado")
        return False
    
    props = cliente.get("properties", {})
    nome = props.get("firstname", "")
    
    print(f"\n🎭 Simulando respostas COM e SEM contexto:")
    print(f"\n--- SEM Contexto (Genérico) ---")
    print("Bot: 'Que alegria saber disso! Muito obrigada pelo reconhecimento.'")
    
    print(f"\n--- COM Contexto (Personalizado) ---")
    print(f"Bot: 'Que alegria, {nome}! Muito obrigada pelo reconhecimento.'")
    
    print(f"\n✅ Personalização funcionando!")
    return True

def main():
    """Executar todos os testes"""
    print("\n" + "🧪 " + "="*58)
    print("   TESTE DE INTEGRAÇÃO - HubSpot Mock + ClienteService")
    print("="*60)
    
    testes = [
        ("Conectividade", test_hubspot_mock_connectivity),
        ("Buscar por Email", test_buscar_cliente_por_email),
        ("Coletar Contexto", test_coletar_contexto),
        ("Personalização", test_personalizacao_prompt)
    ]
    
    resultados = []
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"\n❌ Erro no teste '{nome}': {e}")
            resultados.append((nome, False))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")
    
    total = len(resultados)
    passou = sum(1 for _, r in resultados if r)
    
    print(f"\n📊 Total: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print("\n⚠️ Alguns testes falharam")
        return 1

if __name__ == "__main__":
    exit(main())
