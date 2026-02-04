"""
Agente Avaliador de Resposta
Responsável por classificar respostas NPS e extrair insights

MIGRADO PARA LANGCHAIN: Usa TessLLM wrapper para orquestração via LangChain
"""

from typing import Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from agents.llm.tess_llm import TessLLM


class ResponseEvaluatorAgent:
    def __init__(self):
        # Usar TessLLM via LangChain
        self.llm = TessLLM(temperature=0.7, max_tokens=150)
        self.agent_id = "response-evaluator"
        
        # Prompt template para resumo executivo
        self.summary_prompt = PromptTemplate(
            input_variables=["score", "categoria", "emoji", "sentimento", "feedback", "temas"],
            template="""Você é um analista de experiência do cliente especializado em NPS.

DADOS DA AVALIAÇÃO:
- Score NPS: {score}/10
- Categoria: {categoria}
- Sentimento detectado: {sentimento}
- Feedback textual: "{feedback}"
- Temas identificados: {temas}

TAREFA:
Crie um resumo executivo CONCISO, ESPECÍFICO e ACIONÁVEL desta avaliação NPS.

FORMATO OBRIGATÓRIO:
{emoji} [Classificação] - [Insight principal baseado no feedback]. [Ação sugerida específica].

DIRETRIZES:
- Máximo 2 linhas
- Seja ESPECÍFICO, não genérico
- Mencione detalhes do feedback se houver
- Sugira ação CLARA e ACIONÁVEL
- Use linguagem executiva e direta
- NÃO repita informações óbvias

IMPORTANTE: Retorne APENAS o resumo, sem explicações."""
        )
        
        # Criar chain
        self.summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
    
    @traceable(name="NPS Evaluation")
    def evaluate(self, nps_score: int, feedback_text: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Avalia a resposta de NPS do cliente
        
        Args:
            nps_score: Nota NPS (0-10)
            feedback_text: Texto de feedback opcional
            context: Contexto do cliente (opcional)
            
        Returns:
            Dict com classificação e insights
        """
        print(f"📊 Avaliando resposta NPS: {nps_score}/10...")
        
        start_time = time.time()
        
        # Classificar NPS
        classification = self._classify_nps(nps_score)
        
        # Extrair insights do feedback
        insights = self._extract_insights(feedback_text, nps_score)
        
        # Identificar ações recomendadas
        actions = self._recommend_actions(nps_score, insights, context)
        
        result = {
            "nps_score": nps_score,
            "classificacao": classification,
            "feedback_texto": feedback_text,
            "insights": insights,
            "acoes_recomendadas": actions,
            "prioridade": self._calculate_priority(nps_score, insights),
            "resumo_executivo": self._generate_summary(nps_score, classification, insights, feedback_text, context)
        }
        
        processing_time = (time.time() - start_time) * 1000
        print(f"✅ Avaliação: {classification['categoria']} | Prioridade: {result['prioridade']}")
        
        # 1. Logar interação de avaliação
        contact_id = "unknown"
        if context and context.get("cliente"):
            contact_id = str(context["cliente"].get("id", "unknown"))
            
        supabase_client.log_interaction(
            contact_id=contact_id,
            interaction_type="nps_response_evaluation",
            agent_name="ResponseEvaluatorAgent",
            input_data={"nps_score": nps_score, "feedback": feedback_text},
            output_data=result,
            success=True,
            processing_time_ms=processing_time
        )
        
        # 2. Atualizar tabela de campanhas com a resposta
        # Só atualizamos se tivermos um contact_id válido
        if contact_id != "unknown":
            supabase_client.update_campaign(
                contact_id=contact_id,
                update_data={
                    "nps_score": nps_score,
                    "nps_feedback": feedback_text,
                    "nps_category": classification['categoria'],
                    "response_date": datetime.now().isoformat()
                }
            )
        
        return result

    
    def _classify_nps(self, score: int) -> Dict[str, Any]:
        """Classifica a nota NPS"""
        
        if 0 <= score <= 6:
            return {
                "categoria": "DETRATOR",
                "emoji": "😠",
                "descricao": "Cliente insatisfeito - risco de churn",
                "nps_contribution": -1
            }
        elif 7 <= score <= 8:
            return {
                "categoria": "NEUTRO",
                "emoji": "😐",
                "descricao": "Cliente satisfeito mas não engajado",
                "nps_contribution": 0
            }
        elif 9 <= score <= 10:
            return {
                "categoria": "PROMOTOR",
                "emoji": "🤩",
                "descricao": "Cliente entusiasta - potencial evangelista",
                "nps_contribution": +1
            }
        else:
            return {
                "categoria": "INVALIDO",
                "emoji": "❓",
                "descricao": "Nota fora da escala 0-10",
                "nps_contribution": 0
            }
    
    def _extract_insights(self, feedback: str, score: int) -> Dict[str, Any]:
        """Extrai insights do texto de feedback"""
        
        insights = {
            "sentimento_detectado": "NEUTRO",
            "temas": [],
            "palavras_chave": [],
            "intensidade": "media"
        }
        
        if not feedback:
            insights["sentimento_detectado"] = "AUSENTE"
            return insights
        
        feedback_lower = feedback.lower()
        
        # Detectar sentimento baseado na nota + texto
        palavras_positivas = ["ótimo", "excelente", "maravilhoso", "perfeito", "adorei", 
                             "muito bom", "satisfeito", "recomendo", "parabens", "top"]
        palavras_negativas = ["ruim", "péssimo", "horrível", "decepcionante", "problema",
                             "demora", "lento", "erro", "falha", "insatisfeito", "reclama"]
        
        count_pos = sum(1 for p in palavras_positivas if p in feedback_lower)
        count_neg = sum(1 for p in palavras_negativas if p in feedback_lower)
        
        if score >= 9 and count_pos > count_neg:
            insights["sentimento_detectado"] = "MUITO_POSITIVO"
            insights["intensidade"] = "alta"
        elif score >= 7 and count_pos >= count_neg:
            insights["sentimento_detectado"] = "POSITIVO"
        elif score <= 6 and count_neg > count_pos:
            insights["sentimento_detectado"] = "NEGATIVO"
            insights["intensidade"] = "alta" if count_neg >= 2 else "media"
        elif score <= 6:
            insights["sentimento_detectado"] = "NEGATIVO"
        
        # Extrair temas mencionados
        temas_mapeados = {
            "atendimento": ["atendimento", "suporte", "atendente", "equipe", "gente"],
            "produto": ["produto", "sistema", "plataforma", "software", "ferramenta"],
            "preço": ["preço", "custo", "valor", "caro", "barato", "investimento"],
            "velocidade": ["rápido", "lento", "demora", "tempo", "agilidade", "demorou"],
            "qualidade": ["qualidade", "excelente", "ruim", "bom", "standard"],
            "comunicação": ["comunicação", "resposta", "retorno", "feedback", "contato"]
        }
        
        for tema, palavras in temas_mapeados.items():
            if any(p in feedback_lower for p in palavras):
                insights["temas"].append(tema)
        
        # Identificar palavras-chave relevantes
        palavras_relevantes = []
        for palavra in feedback.split():
            if len(palavra) > 4 and palavra.lower() not in ["muito", "para", "como", "esta", "este", "essa", "esse"]:
                palavras_relevantes.append(palavra)
        
        insights["palavras_chave"] = palavras_relevantes[:5]  # Top 5
        
        return insights
    
    def _recommend_actions(self, score: int, insights: Dict, context: Optional[Dict]) -> list:
        """Recomenda ações baseadas na avaliação"""
        
        acoes = []
        
        if score <= 6:
            # Detrator
            acoes.append({
                "tipo": "alerta",
                "acao": "Contato imediato do CS - entender problema",
                "urgencia": "alta",
                "responsavel": "Customer Success"
            })
            
            if insights.get("temas"):
                for tema in insights["temas"][:2]:
                    acoes.append({
                        "tipo": "melhoria",
                        "acao": f"Revisar {tema} - identificado como problema",
                        "urgencia": "media",
                        "responsavel": "Product/Operations"
                    })
            
            acoes.append({
                "tipo": "recuperacao",
                "acao": "Oferecer compensação/benefício para recuperar confiança",
                "urgencia": "media",
                "responsavel": "CS Manager"
            })
            
        elif score <= 8:
            # Neutro
            acoes.append({
                "tipo": "engajamento",
                "acao": "Enviar material sobre novidades/features não utilizadas",
                "urgencia": "baixa",
                "responsavel": "Marketing"
            })
            
            acoes.append({
                "tipo": "pesquisa",
                "acao": "Follow-up qualitativo: o que falta para nota 10?",
                "urgencia": "baixa",
                "responsavel": "CS"
            })
            
        else:
            # Promotor
            acoes.append({
                "tipo": "celebracao",
                "acao": "Agradecimento personalizado do CEO/founder",
                "urgencia": "baixa",
                "responsavel": "Leadership"
            })
            
            acoes.append({
                "tipo": "advocacia",
                "acao": "Convidar para programa de embaixador/referência",
                "urgencia": "baixa",
                "responsavel": "Marketing"
            })
            
            acoes.append({
                "tipo": "depoimento",
                "acao": "Solicitar case study/depoimento para site",
                "urgencia": "baixa",
                "responsavel": "Marketing"
            })
        
        return acoes
    
    def _calculate_priority(self, score: int, insights: Dict) -> str:
        """Calcula prioridade de tratamento"""
        
        if score <= 4:
            return "URGENTE"
        elif score <= 6:
            return "ALTA"
        elif score <= 8 and insights.get("intensidade") == "alta":
            return "MEDIA"
        elif score <= 8:
            return "BAIXA"
        else:
            return "BAIXA"
    
    def _generate_summary(self, score: int, classification: Dict, insights: Dict, feedback_text: str = "", context: Optional[Dict] = None) -> str:
        """
        Gera resumo executivo da avaliação usando LangChain
        
        Usa TessLLM via LangChain chain para geração estruturada
        """
        
        categoria = classification["categoria"]
        emoji = classification["emoji"]
        sentimento = insights.get("sentimento_detectado", "AUSENTE")
        temas = insights.get("temas", [])
        
        try:
            # Executar LangChain chain
            resumo = self.summary_chain.run(
                score=score,
                categoria=categoria,
                emoji=emoji,
                sentimento=sentimento,
                feedback=feedback_text if feedback_text else "Sem feedback textual",
                temas=", ".join(temas) if temas else "Nenhum"
            )
            
            print(f"✅ Resumo executivo gerado via LangChain")
            return resumo.strip()
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar resumo via LangChain: {e}")
            print("📝 Usando fallback para template padrão")
            return self._generate_fallback_summary(score, categoria, emoji, sentimento, temas)
    
    def _generate_fallback_summary(self, score: int, categoria: str, emoji: str, sentimento: str, temas: list) -> str:
        """Resumo de fallback caso o LLM falhe"""
        
        if categoria == "DETRATOR":
            return f"{emoji} Cliente DETRATOR ({score}/10) - REQUER AÇÃO IMEDIATA. " \
                   f"Sentimento: {sentimento}. " \
                   f"Temas: {', '.join(temas) if temas else 'Nenhum identificado'}."
        
        elif categoria == "NEUTRO":
            return f"{emoji} Cliente NEUTRO ({score}/10) - Oportunidade de engajamento. " \
                   f"Sentimento: {sentimento}. " \
                   f"Potencial de conversão para Promotor."
        
        elif categoria == "PROMOTOR":
            return f"{emoji} Cliente PROMOTOR ({score}/10) - Excelente! " \
                   f"Sentimento: {sentimento}. " \
                   f"Candidato a programa de advocacia."
        
        else:
            return f"❓ Nota inválida ({score}) - Verificar resposta."

    
    def batch_evaluate(self, responses: list) -> Dict[str, Any]:
        """Avalia múltiplas respostas e gera métricas consolidadas"""
        
        total = len(responses)
        if total == 0:
            return {"error": "Nenhuma resposta para avaliar"}
        
        detrators = sum(1 for r in responses if 0 <= r.get("score", -1) <= 6)
        neutrals = sum(1 for r in responses if 7 <= r.get("score", -1) <= 8)
        promoters = sum(1 for r in responses if 9 <= r.get("score", -1) <= 10)
        
        nps_score = ((promoters - detrators) / total) * 100
        
        return {
            "total_respostas": total,
            "detrators": detrators,
            "neutrals": neutrals,
            "promoters": promoters,
            "nps_score": round(nps_score, 1),
            "distribuicao": {
                "detrators_pct": round((detrators/total)*100, 1),
                "neutrals_pct": round((neutrals/total)*100, 1),
                "promoters_pct": round((promoters/total)*100, 1)
            }
        }


if __name__ == "__main__":
    print("🧪 Testando Agente Avaliador de Resposta")
    print("=" * 60)
    
    evaluator = ResponseEvaluatorAgent()
    
    # Testar diferentes cenários
    testes = [
        {"score": 3, "feedback": "Muito insatisfeito com o atendimento. Demora demais para resolver."},
        {"score": 7, "feedback": "Bom serviço mas poderia ser mais rápido."},
        {"score": 10, "feedback": "Excelente! Adoro trabalhar com vocês. Sistema perfeito!"}
    ]
    
    for teste in testes:
        print(f"\n{'='*60}")
        print(f"Teste: Nota {teste['score']}/10")
        print(f"Feedback: {teste['feedback']}")
        print("-" * 60)
        
        resultado = evaluator.evaluate(teste["score"], teste["feedback"])
        
        print(f"Classificação: {resultado['classificacao']['emoji']} {resultado['classificacao']['categoria']}")
        print(f"Descrição: {resultado['classificacao']['descricao']}")
        print(f"Prioridade: {resultado['prioridade']}")
        print(f"\nResumo:")
        print(resultado['resumo_executivo'])
        
        print(f"\nAções Recomendadas:")
        for acao in resultado['acoes_recomendadas'][:2]:
            print(f"  • [{acao['urgencia'].upper()}] {acao['acao']} ({acao['responsavel']})")
    
    # Testar métricas batch
    print("\n" + "="*60)
    print("📊 Teste de Métricas em Lote:")
    sample_responses = [
        {"score": 10}, {"score": 9}, {"score": 8}, 
        {"score": 7}, {"score": 5}, {"score": 3}
    ]
    metrics = evaluator.batch_evaluate(sample_responses)
    print(f"Total: {metrics['total_respostas']}")
    print(f"NPS Score: {metrics['nps_score']}")
    print(f"Promotores: {metrics['promoters']} ({metrics['distribuicao']['promoters_pct']}%)")
    print(f"Neutros: {metrics['neutrals']} ({metrics['distribuicao']['neutrals_pct']}%)")
    print(f"Detratores: {metrics['detrators']} ({metrics['distribuicao']['detrators_pct']}%)")
