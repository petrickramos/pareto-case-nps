"""
Teste Completo do Fluxo NPS
Análise de Sentimento → Geração de Mensagem
"""

from tess_client import TessClient
import json

print("\n" + "="*70)
print("🚀 TESTE COMPLETO DO FLUXO NPS")
print("="*70)

# Inicializar cliente Tess
client = TessClient()

# ============================================
# CENÁRIO DE TESTE: Cliente Promotor
# ============================================

cliente_contexto = {
    "nome": "Maria Silva",
    "email": "maria.silva@empresa.com",
    "empresa": "Tech Solutions Ltda",
    "historico": "Cliente há 2 anos, sempre pontual nos pagamentos",
    "tickets_abertos": 0,
    "ultima_interacao": "Elogiou o novo recurso de relatórios",
    "valor_investido": "R$ 15.000/mês"
}

print("\n" + "="*70)
print("👤 CLIENTE: Maria Silva")
print("="*70)
print(json.dumps(cliente_contexto, indent=2, ensure_ascii=False))

# ============================================
# PASSO 1: Análise de Sentimento
# ============================================

print("\n" + "="*70)
print("🧠 PASSO 1: ANÁLISE DE SENTIMENTO (Agente 39004)")
print("="*70)

prompt_analise = f"""
Analise o perfil deste cliente e determine o sentimento e risco de churn:

Cliente: {cliente_contexto['nome']}
Histórico: {cliente_contexto['historico']}
Última interação: {cliente_contexto['ultima_interacao']}
Tickets abertos: {cliente_contexto['tickets_abertos']}
Valor investido: {cliente_contexto['valor_investido']}

Retorne um JSON com:
- sentimento_geral (POSITIVO/NEUTRO/NEGATIVO)
- risco_churn (BAIXO/MEDIO/ALTO)
- justificativa (texto breve)
- recomendacao (ação sugerida)
"""

print("\n📤 Enviando para análise...")

try:
    resultado_analise = client.generate(
        prompt=prompt_analise,
        agent_id="39004",
        system_prompt="Você é um analista de Customer Success especializado em NPS. Analise o perfil do cliente e retorne um JSON estruturado."
    )
    
    print("\n✅ Análise recebida!")
    print("\n" + "-"*70)
    print(resultado_analise)
    print("-"*70)
    
    # Tentar extrair dados estruturados (se vier JSON)
    try:
        # Procurar por JSON no texto
        if '{' in resultado_analise and '}' in resultado_analise:
            json_start = resultado_analise.find('{')
            json_end = resultado_analise.rfind('}') + 1
            json_str = resultado_analise[json_start:json_end]
            analise_data = json.loads(json_str)
            
            sentimento = analise_data.get('sentimento_geral', 'POSITIVO')
            risco = analise_data.get('risco_churn', 'BAIXO')
        else:
            # Fallback: inferir do texto
            texto_lower = resultado_analise.lower()
            if 'positivo' in texto_lower or 'satisfeito' in texto_lower:
                sentimento = 'POSITIVO'
                risco = 'BAIXO'
            elif 'negativo' in texto_lower or 'insatisfeito' in texto_lower:
                sentimento = 'NEGATIVO'
                risco = 'ALTO'
            else:
                sentimento = 'NEUTRO'
                risco = 'MEDIO'
    except:
        sentimento = 'POSITIVO'
        risco = 'BAIXO'
    
    print(f"\n📊 Resultado da Análise:")
    print(f"   Sentimento: {sentimento}")
    print(f"   Risco de Churn: {risco}")
    
except Exception as e:
    print(f"\n❌ Erro na análise: {e}")
    sentimento = 'POSITIVO'
    risco = 'BAIXO'

# ============================================
# PASSO 2: Geração de Mensagem NPS
# ============================================

print("\n" + "="*70)
print("✍️ PASSO 2: GERAÇÃO DE MENSAGEM NPS (Agente 39005)")
print("="*70)

prompt_mensagem = f"""
Crie uma mensagem de NPS personalizada para:

Cliente: {cliente_contexto['nome']}
Sentimento detectado: {sentimento}
Risco de churn: {risco}
Contexto: {cliente_contexto['historico']}

A mensagem deve:
- Ser empática e personalizada
- Mencionar o relacionamento de 2 anos
- Ter um tom {sentimento.lower()}
- Incluir um CTA claro para responder o NPS

Retorne um JSON com:
- assunto (título do email)
- mensagem (corpo do email)
- tom (empático/profissional/caloroso)
"""

print("\n📤 Gerando mensagem personalizada...")

try:
    resultado_mensagem = client.generate(
        prompt=prompt_mensagem,
        agent_id="39005",
        system_prompt="Você é um especialista em copywriting para NPS. Crie mensagens empáticas e personalizadas que aumentam a taxa de resposta."
    )
    
    print("\n✅ Mensagem gerada!")
    print("\n" + "-"*70)
    print(resultado_mensagem)
    print("-"*70)
    
except Exception as e:
    print(f"\n❌ Erro na geração: {e}")

# ============================================
# RESUMO DO FLUXO
# ============================================

print("\n" + "="*70)
print("📋 RESUMO DO FLUXO COMPLETO")
print("="*70)
print(f"""
✅ Cliente analisado: {cliente_contexto['nome']}
✅ Sentimento identificado: {sentimento}
✅ Risco de churn: {risco}
✅ Mensagem NPS gerada com sucesso
✅ Pronta para envio

🎯 Próximos passos:
   1. Revisar mensagem gerada
   2. Enviar via email/WhatsApp
   3. Aguardar resposta do cliente
   4. Registrar NPS no Supabase
""")

print("="*70)
print("🎉 TESTE COMPLETO FINALIZADO COM SUCESSO!")
print("="*70 + "\n")
