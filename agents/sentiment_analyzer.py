"""
Agente Analisador de Sentimento
Responsável por analisar o contexto do cliente e identificar sentimento/riscos
"""

import json
from typing import Dict, Any
import time
from datetime import datetime
from langsmith import traceable
from tess_client import TessClient
from supabase_client import supabase_client


class SentimentAnalyzerAgent:
    def __init__(self):
        self.tess = TessClient()
        # ID do agente de análise de sentimento na Tess (ajustar conforme disponível)
        self.agent_id = "sentiment-analyzer"  # Placeholder, ajustar após verificar na Tess
    
    @traceable(name="Sentiment Analysis")
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa o contexto do cliente e retorna sentimento + riscos
        
        Args:
            context: Contexto formatado do cliente (vindo do ContextCollector)
            
        Returns:
            Dict com análise de sentimento e riscos
        """
        print("🧠 Analisando sentimento e riscos do cliente...")
        
        start_time = time.time()
        success = True
        error_msg = None
        analysis = {}
        
        # Construir prompt de análise
        prompt = self._build_analysis_prompt(context)
        
        # Tentar usar Tess API se disponível, senão fazer análise local
        try:
            # Verificar se há agente específico na Tess
            result = self.tess.execute_agent(self.agent_id, {"prompt": prompt})
            if result:
                analysis = result.get("response", {})
            else:
                # Análise local fallback
                analysis = self._local_analysis(context)
        except Exception as e:
            # Fallback para análise local
            print(f"⚠️ Erro na análise remota: {e}. Usando fallback.")
            analysis = self._local_analysis(context)
            # Mesmo usando fallback, queremos saber que deu erro na principal
            # Mas marcamos success=True pois recuperamos com fallback. 
            # O erro_msg fica registrado pra debug
            error_msg = str(e)
        
        processing_time = (time.time() - start_time) * 1000
        print(f"✅ Análise concluída: Sentimento {analysis.get('sentimento_geral', 'N/A')}")
        
        # Logar interação no Supabase
        supabase_client.log_interaction(
            contact_id=context.get("cliente", {}).get("id", "unknown"),
            interaction_type="sentiment_analysis",
            agent_name="SentimentAnalyzerAgent",
            input_data={"context_summary": "Contexto completo do cliente", "prompt_len": len(prompt)},
            output_data=analysis,
            success=success,
            error_message=error_msg,
            processing_time_ms=processing_time
        )
        
        return analysis
    
    def _build_analysis_prompt(self, context: Dict) -> str:
        """Constrói prompt para análise de sentimento"""
        
        cliente = context.get("cliente", {})
        metricas = context.get("metricas", {})
        
        prompt = f"""Analise o seguinte perfil de cliente e determine o sentimento e riscos:

CLIENTE: {cliente.get('nome', 'N/A')}
Tempo como cliente: {cliente.get('tempo_como_cliente', 'N/A')}
Valor total em negócios: R$ {metricas.get('valor_total', 0):,.2f}

HISTÓRICO:
- Negócios ({metricas.get('quantidade_deals', 0)}):
"""
        
        for deal in context.get("negocios", [])[:3]:
            prompt += f"  • {deal['nome']} - R$ {deal['valor']:,.2f} ({deal['fase']})\n"
        
        prompt += f"\n- Tickets/Chamados ({metricas.get('quantidade_tickets', 0)}):\n"
        for ticket in context.get("tickets", [])[:3]:
            prompt += f"  • {ticket['assunto']} - {ticket['categoria']}\n"
        
        if context.get("riscos"):
            prompt += "\nRISCOS IDENTIFICADOS:\n"
            for risco in context["riscos"][:3]:
                prompt += f"  • {risco['description']}\n"
        
        prompt += """\nAnalise considerando:
1. Tempo como cliente (quanto mais tempo, mais engajado)
2. Valor dos negócios (cliente de alto valor = prioridade)
3. Tickets abertos (indicadores de insatisfação)
4. Padrão de comunicação recente

Retorne um JSON com:
{
  "sentimento_geral": "POSITIVO/NEUTRO/NEGATIVO",
  "nivel_satisfacao": 1-10,
  "risco_churn": "BAIXO/MEDIO/ALTO",
  "justificativa": "explicação breve",
  "recomendacao": "como abordar este cliente"
}"""
        
        return prompt
    
    def _local_analysis(self, context: Dict) -> Dict[str, Any]:
        """Análise local de sentimento (fallback)"""
        
        metricas = context.get("metricas", {})
        riscos = context.get("riscos", [])
        tickets = context.get("tickets", [])
        
        # Lógica de análise simplificada
        score = 5  # Neutro base
        
        # Ajustar por valor (clientes de alto valor tendem a ser mais engajados)
        valor_total = metricas.get("valor_total", 0)
        if valor_total > 50000:
            score += 2
        elif valor_total > 10000:
            score += 1
        elif valor_total < 1000:
            score -= 1
        
        # Ajustar por tickets abertos
        num_tickets = metricas.get("quantidade_tickets", 0)
        if num_tickets == 0:
            score += 2  # Sem tickets = bom sinal
        elif num_tickets >= 3:
            score -= 2  # Muitos tickets = alerta
        
        # Ajustar por riscos identificados
        num_riscos = len(riscos)
        if num_riscos > 0:
            score -= num_riscos * 2
        
        # Limitar score entre 1-10
        score = max(1, min(10, score))
        
        # Determinar sentimento
        if score >= 8:
            sentimento = "POSITIVO"
            risco_churn = "BAIXO"
        elif score >= 5:
            sentimento = "NEUTRO"
            risco_churn = "MEDIO"
        else:
            sentimento = "NEGATIVO"
            risco_churn = "ALTO"
        
        # Construir justificativa
        justificativas = []
        if valor_total > 0:
            justificativas.append(f"Cliente com R$ {valor_total:,.2f} em negócios")
        if num_tickets > 0:
            justificativas.append(f"Possui {num_tickets} ticket(s) aberto(s)")
        if num_riscos > 0:
            justificativas.append(f"{num_riscos} risco(s) identificado(s)")
        
        justificativa = "; ".join(justificativas) if justificativas else "Perfil de cliente regular"
        
        # Recomendação
        if risco_churn == "ALTO":
            recomendacao = "Abordagem cuidadosa. Priorizar resolução de tickets antes de enviar pesquisa."
        elif risco_churn == "MEDIO":
            recomendacao = "Abordagem padrão com tom empático. Verificar satisfação recente."
        else:
            recomendacao = "Abordagem otimista. Cliente engajado, boa oportunidade para depoimento."
        
        return {
            "sentimento_geral": sentimento,
            "nivel_satisfacao": score,
            "risco_churn": risco_churn,
            "justificativa": justificativa,
            "recomendacao": recomendacao,
            "fatores_positivos": self._extract_positive_factors(context),
            "fatores_negativos": self._extract_negative_factors(context)
        }
    
    def _extract_positive_factors(self, context: Dict) -> list:
        """Extrai fatores positivos do contexto"""
        positivos = []
        
        if context["metricas"].get("valor_total", 0) > 10000:
            positivos.append("Cliente de alto valor")
        
        if context["metricas"].get("quantidade_tickets", 0) == 0:
            positivos.append("Sem tickets abertos")
        
        if context["metricas"].get("quantidade_deals", 0) >= 2:
            positivos.append("Múltiplos negócios fechados")
        
        if not context.get("riscos"):
            positivos.append("Sem riscos identificados")
        
        return positivos
    
    def _extract_negative_factors(self, context: Dict) -> list:
        """Extrai fatores negativos/riscos do contexto"""
        negativos = []
        
        for risco in context.get("riscos", []):
            negativos.append(risco.get("description", "Risco identificado"))
        
        if context["metricas"].get("quantidade_tickets", 0) >= 2:
            negativos.append(f"{context['metricas']['quantidade_tickets']} tickets abertos")
        
        return negativos


if __name__ == "__main__":
    print("🧪 Testando Agente Analisador de Sentimento")
    print("=" * 60)
    
    from agents.context_collector import ContextCollectorAgent
    
    # Coletar contexto primeiro
    collector = ContextCollectorAgent()
    context = collector.collect("101")
    
    # Analisar
    analyzer = SentimentAnalyzerAgent()
    analysis = analyzer.analyze(context)
    
    print("\n📊 Análise de Sentimento:")
    print(f"Sentimento Geral: {analysis['sentimento_geral']}")
    print(f"Nível de Satisfação: {analysis['nivel_satisfacao']}/10")
    print(f"Risco de Churn: {analysis['risco_churn']}")
    print(f"\nJustificativa: {analysis['justificativa']}")
    print(f"\nRecomendação: {analysis['recomendacao']}")
    
    if analysis.get('fatores_positivos'):
        print("\n✅ Fatores Positivos:")
        for fator in analysis['fatores_positivos']:
            print(f"  • {fator}")
    
    if analysis.get('fatores_negativos'):
        print("\n⚠️ Fatores Negativos:")
        for fator in analysis['fatores_negativos']:
            print(f"  • {fator}")
