"""
Sistema Multi-Agente NPS - Case Pareto
Orquestra o fluxo completo de pesquisa de satisfação
"""

import sys
sys.path.append('/Users/julianamoraesferreira/Documents/Projetos-Dev-Petrick/pareto-case/langchain')

from agents.context_collector import ContextCollectorAgent
from agents.sentiment_analyzer import SentimentAnalyzerAgent
from agents.message_generator import MessageGeneratorAgent
from agents.response_evaluator import ResponseEvaluatorAgent


def run_nps_flow(contact_id: str, generate_message: bool = True) -> dict:
    """
    Executa o fluxo completo de NPS para um contato
    
    Fluxo:
    1. Coleta contexto do cliente (HubSpot)
    2. Analisa sentimento e riscos
    3. Gera mensagem personalizada (opcional)
    
    Args:
        contact_id: ID do contato no HubSpot
        generate_message: Se deve gerar mensagem de NPS
        
    Returns:
        Dict com resultado completo do fluxo
    """
    print("🚀 Iniciando Fluxo NPS Multi-Agente")
    print("=" * 70)
    print(f"📌 Contato ID: {contact_id}")
    print("=" * 70)
    
    # ETAPA 1: Coletar Contexto
    print("\n📋 ETAPA 1: Coleta de Contexto")
    print("-" * 70)
    collector = ContextCollectorAgent()
    context = collector.collect(contact_id, days_back=30)
    
    if not context:
        return {"error": "Falha ao coletar contexto do cliente"}
    
    cliente = context.get("cliente", {}) if isinstance(context.get("cliente"), dict) else {}
    metricas = context.get("metricas", {}) if isinstance(context.get("metricas"), dict) else {}
    print(f"\n✅ Contexto coletado:")
    print(f"   Cliente: {cliente.get('nome', 'N/A')}")
    print(f"   Email: {cliente.get('email', 'N/A')}")
    print(f"   Tempo: {cliente.get('tempo_como_cliente', 'N/A')}")
    print(f"   Valor Total: R$ {metricas.get('valor_total', 0):,.2f}")
    print(f"   Deals: {metricas.get('quantidade_deals', 0)}")
    print(f"   Tickets: {metricas.get('quantidade_tickets', 0)}")
    print(f"   Riscos: {metricas.get('riscos_identificados', 0)}")
    
    # ETAPA 2: Analisar Sentimento
    print("\n🧠 ETAPA 2: Análise de Sentimento")
    print("-" * 70)
    analyzer = SentimentAnalyzerAgent()
    analysis = analyzer.analyze(context)
    
    print(f"\n✅ Análise concluída:")
    print(f"   Sentimento: {analysis.get('sentimento_geral', 'N/A')}")
    print(f"   Satisfação: {analysis.get('nivel_satisfacao', 'N/A')}/10")
    print(f"   Risco Churn: {analysis.get('risco_churn', 'N/A')}")
    print(f"   Justificativa: {analysis.get('justificativa', 'N/A')}")
    
    resultado = {
        "contact_id": contact_id,
        "contexto": context,
        "analise": analysis
    }
    
    # ETAPA 3: Gerar Mensagem (opcional)
    if generate_message:
        print("\n✉️  ETAPA 3: Geração de Mensagem NPS")
        print("-" * 70)
        generator = MessageGeneratorAgent()
        message = generator.generate(context, analysis)
        
        resultado["mensagem_nps"] = message
        
        print(f"\n✅ Mensagem gerada:")
        print(f"   Tom: {message.get('tom', 'N/A')}")
        print(f"   Tipo: {message.get('tipo', 'N/A')}")
        print(f"   Assunto: {message.get('assunto', 'N/A')}")
        print(f"\n   Preview da mensagem:")
        print("   " + "-" * 50)
        preview = message.get('mensagem', '')[:200]
        print(f"   {preview}...")
        print("   " + "-" * 50)
    
    # Resumo Final
    print("\n" + "=" * 70)
    print("✅ FLUXO NPS CONCLUÍDO COM SUCESSO")
    print("=" * 70)
    print(f"\n📊 Resumo:")
    print(f"   Cliente: {cliente.get('nome', 'N/A')} ({contact_id})")
    print(f"   Perfil: {analysis.get('sentimento_geral', 'N/A')} | Risco: {analysis.get('risco_churn', 'N/A')}")
    print(f"   Recomendação: {analysis.get('recomendacao', 'N/A')}")
    
    return resultado


def simulate_nps_response(contact_id: str, nps_score: int, feedback: str = ""):
    """
    Simula uma resposta de NPS e avalia
    
    Args:
        contact_id: ID do contato
        nps_score: Nota NPS (0-10)
        feedback: Texto de feedback
    """
    print("\n📝 Simulando Resposta de NPS")
    print("=" * 70)
    print(f"Contato: {contact_id}")
    print(f"Nota: {nps_score}/10")
    print(f"Feedback: {feedback or '(sem feedback)'}")
    print("-" * 70)
    
    evaluator = ResponseEvaluatorAgent()
    resultado = evaluator.evaluate(nps_score, feedback)
    
    print(f"\n📊 Avaliação:")
    print(f"   Classificação: {resultado['classificacao']['emoji']} {resultado['classificacao']['categoria']}")
    print(f"   Descrição: {resultado['classificacao']['descricao']}")
    print(f"   Prioridade: {resultado['prioridade']}")
    
    insights = resultado.get('insights', {}) if isinstance(resultado.get('insights'), dict) else {}
    if insights.get('temas'):
        print(f"\n   Temas identificados: {', '.join(insights['temas'])}")
    
    print(f"\n🎯 Ações recomendadas:")
    for acao in resultado['acoes_recomendadas']:
        print(f"   • [{acao['tipo'].upper()}] {acao['acao']}")
    
    return resultado


def main():
    """Função principal para teste"""
    print("🎯 Sistema Multi-Agente NPS - Case Pareto")
    print("=" * 70)
    print()
    
    # Testar com contact_id 101
    contact_id = "101"
    
    # Executar fluxo completo
    resultado = run_nps_flow(contact_id, generate_message=True)
    
    # Simular resposta do cliente
    print("\n" + "=" * 70)
    print("🧪 SIMULAÇÃO DE RESPOSTA DO CLIENTE")
    print("=" * 70)
    
    # Simular diferentes tipos de respostas
    simulacoes = [
        {"score": 9, "feedback": "Muito satisfeito com o atendimento!"},
        {"score": 6, "feedback": "O sistema é bom mas às vezes trava."}
    ]
    
    for sim in simulacoes:
        simulate_nps_response(contact_id, sim["score"], sim["feedback"])
        print("\n")
    
    print("\n" + "=" * 70)
    print("🏁 FIM DOS TESTES")
    print("=" * 70)


if __name__ == "__main__":
    main()
