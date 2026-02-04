"""
Agente Gerador de Mensagem
Responsável por criar mensagens personalizadas de pesquisa NPS

MIGRADO PARA LANGCHAIN: Usa TessLLM wrapper para orquestração via LangChain
"""

from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from agents.llm.tess_llm import TessLLM
from datetime import datetime


class MessageGeneratorAgent:
    def __init__(self):
        # Usar TessLLM via LangChain
        self.llm = TessLLM(temperature=0.8, max_tokens=300)
        self.agent_id = "message-generator"
        
        # Prompt template estruturado
        self.message_prompt = PromptTemplate(
            input_variables=["nome", "sentimento", "risco", "tom", "objetivo", "contexto"],
            template="""Você é um assistente de relacionamento com clientes da Pareto, uma empresa de consultoria estratégica.

CONTEXTO DO CLIENTE:
- Nome: {nome}
- Sentimento detectado: {sentimento}
- Nível de risco de churn: {risco}
{contexto}

TAREFA:
Escreva uma mensagem NATURAL e PERSONALIZADA convidando {nome} a avaliar sua experiência através de uma pesquisa NPS (escala de 0 a 10).

DIRETRIZES:
- Tom: {tom}
- Objetivo: {objetivo}
- Seja breve (máximo 4-5 linhas)
- Mencione algo específico do histórico do cliente se relevante
- Evite linguagem corporativa genérica ou clichês
- Use uma saudação natural e uma despedida apropriada ao tom
- NÃO use emojis
- Inclua [LINK_PESQUISA] onde o link da pesquisa deve aparecer

IMPORTANTE: 
- Retorne APENAS a mensagem, sem explicações ou comentários
- A mensagem deve parecer escrita por uma pessoa real, não por um robô
- Varie o vocabulário e a estrutura das frases
"""
        )
        
        # Criar chain
        self.message_chain = LLMChain(llm=self.llm, prompt=self.message_prompt)
    
    @traceable(name="Message Generation")
    def generate(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera mensagem personalizada de pesquisa NPS
        
        Args:
            context: Contexto do cliente
            analysis: Análise de sentimento e riscos
            
        Returns:
            Dict com mensagem completa e metadata
        """
        print("✍️ Gerando mensagem personalizada de NPS...")
        import time
        
        start_time = time.time()
        
        cliente = context.get("cliente", {})
        contact_id = str(cliente.get("id", "unknown"))
        sentimento = analysis.get("sentimento_geral", "NEUTRO")
        risco = analysis.get("risco_churn", "MEDIO")
        
        # Usar LLM para gerar mensagem personalizada
        try:
            mensagem = self._generate_llm_message(context, analysis)
        except Exception as e:
            # Fallback seguro caso algo muito errado aconteça no wrapper
            print(f"Erro grave na geração LLM: {e}")
            mensagem = self._generate_fallback_message(cliente.get("nome", "Cliente"), sentimento, risco)
        
        result = {
            "tipo": "NPS",
            "tom": "cuidadoso" if risco == "ALTO" else "padrão" if sentimento == "NEUTRO" else "entusiasta",
            "assunto": self._generate_subject(context, analysis),
            "mensagem": mensagem,
            "contexto_usado": {
                "cliente": cliente.get("nome"),
                "valor_total": context.get("metricas", {}).get("valor_total"),
                "sentimento": sentimento,
                "risco": risco
            }
        }
        
        processing_time = (time.time() - start_time) * 1000
        print(f"✅ Mensagem gerada: Tom {result['tom']}")
        
        # 1. Logar interação de geração de mensagem
        supabase_client.log_interaction(
            contact_id=contact_id,
            interaction_type="message_generation",
            agent_name="MessageGeneratorAgent",
            input_data={"analysis": analysis},
            output_data=result,
            success=True,
            processing_time_ms=processing_time
        )
        
        # 2. Atualizar tabela de campanhas
        # Registramos o início da campanha com os dados que já temos
        supabase_client.update_campaign(
            contact_id=contact_id,
            update_data={
                "contact_name": cliente.get("nome"),
                "contact_email": cliente.get("email"),
                "sentiment_score": sentimento,
                "risk_level": risco,
                "message_sent": True, # Assumimos enviado após geração neste fluxo
                "message_subject": result["assunto"],
                "message_content": mensagem,
                "message_tone": result["tom"],
                "campaign_date": datetime.now().isoformat()
            }
        )
        
        return result

    
    def _generate_llm_message(self, context: Dict, analysis: Dict) -> str:
        """
        Gera mensagem personalizada usando LangChain
        
        Usa TessLLM via LangChain chain para geração estruturada
        """
        
        cliente = context.get("cliente", {})
        metricas = context.get("metricas", {})
        nome = cliente.get("nome", "Cliente").split()[0]
        sentimento = analysis.get("sentimento_geral", "NEUTRO")
        risco = analysis.get("risco_churn", "MEDIO")
        
        # Determinar tom baseado no perfil
        if risco == "ALTO" or sentimento == "NEGATIVO":
            tom = "empático e cuidadoso"
            objetivo = "recuperar a confiança e entender frustrações"
        elif sentimento == "POSITIVO":
            tom = "entusiasta e caloroso"
            objetivo = "celebrar a parceria e fortalecer o relacionamento"
        else:
            tom = "profissional e amigável"
            objetivo = "coletar feedback construtivo"
        
        # Enriquecer contexto com dados relevantes
        contexto_resumido = self._summarize_context(context, analysis)
        
        # Adicionar métricas ao contexto
        contexto_completo = f"""- Valor total em negócios: R$ {metricas.get('valor_total', 0):,.2f}
- Tempo como cliente: {cliente.get('tempo_como_cliente', 'Não especificado')}
{contexto_resumido}"""

        try:
            # Executar LangChain chain
            mensagem = self.message_chain.run(
                nome=nome,
                sentimento=sentimento,
                risco=risco,
                tom=tom,
                objetivo=objetivo,
                contexto=contexto_completo
            )
            
            print(f"✅ Mensagem LLM gerada via LangChain (tom: {tom})")
            return mensagem.strip()
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar mensagem via LangChain: {e}")
            print("📝 Usando fallback para template padrão")
            return self._generate_fallback_message(nome, sentimento, risco)
    
    def _summarize_context(self, context: Dict, analysis: Dict) -> str:
        """Cria um resumo do contexto para enriquecer o prompt"""
        
        resumo_parts = []
        
        # Deals recentes
        deals = context.get("deals", [])
        if deals:
            deal_recente = deals[0]
            resumo_parts.append(f"- Último negócio: {deal_recente.get('titulo', 'N/A')}")
        
        # Tickets abertos
        tickets = context.get("tickets", [])
        if tickets:
            tickets_abertos = [t for t in tickets if t.get("status") == "ABERTO"]
            if tickets_abertos:
                resumo_parts.append(f"- Tickets abertos: {len(tickets_abertos)}")
        
        # Fatores positivos/negativos da análise
        if analysis.get("fatores_positivos"):
            resumo_parts.append(f"- Pontos fortes: {', '.join(analysis['fatores_positivos'][:2])}")
        
        if analysis.get("fatores_negativos"):
            resumo_parts.append(f"- Pontos de atenção: {', '.join(analysis['fatores_negativos'][:2])}")
        
        return "\n".join(resumo_parts) if resumo_parts else "- Sem histórico recente disponível"
    
    def _generate_fallback_message(self, nome: str, sentimento: str, risco: str) -> str:
        """Mensagem de fallback caso o LLM falhe"""
        
        if risco == "ALTO" or sentimento == "NEGATIVO":
            return f"""Olá {nome},

Esperamos que esteja bem. Notamos que você teve algumas interações recentes conosco e queremos garantir que sua experiência tenha sido a melhor possível.

Sua opinião é muito importante para continuarmos melhorando. Poderia dedicar 1 minuto para nos contar como foi sua experiência?

Acesse a pesquisa aqui: [LINK_PESQUISA]

Agradecemos sua paciência e confiança em nossa parceria.

Atenciosamente,
Equipe Pareto"""
        
        elif sentimento == "POSITIVO":
            return f"""Olá {nome},

Você é um cliente importante para nós! Gostaríamos de ouvir sua opinião sobre como podemos ser ainda melhores.

Responda nossa pesquisa rápida (só 1 minuto): [LINK_PESQUISA]

Agradecemos por fazer parte da nossa história!

Um abraço,
Equipe Pareto"""
        
        else:
            return f"""Olá {nome},

Como parte do nosso compromisso contínuo com a excelência, gostaríamos de ouvir sua opinião sobre nossos serviços.

Poderia responder nossa pesquisa rápida? Leva apenas 1 minuto: [LINK_PESQUISA]

Agradecemos sua participação!

Atenciosamente,
Equipe Pareto"""

    
    def _generate_subject(self, context: Dict, analysis: Dict) -> str:
        """Gera linha de assunto personalizada"""
        
        sentimento = analysis.get("sentimento_geral", "NEUTRO")
        risco = analysis.get("risco_churn", "MEDIO")
        
        if risco == "ALTO":
            return "Sua opinião é importante para melhorarmos sua experiência"
        elif sentimento == "POSITIVO":
            return "Ajude-nos a sermos ainda melhores para você 💪"
        else:
            return "Pesquisa rápida: como podemos melhorar?"
    
    def generate_nps_question(self) -> str:
        """Retorna a pergunta NPS padrão"""
        return "Em uma escala de 0 a 10, quanto você recomendaria nossa empresa para um amigo ou colega?"
    
    def generate_follow_up_questions(self, score: int) -> list:
        """Gera perguntas de follow-up baseadas na nota NPS"""
        
        if score >= 9:
            # Promotor
            return [
                "Qual o principal motivo da sua nota?",
                "O que mais gosta em nossa parceria?"
            ]
        elif score >= 7:
            # Neutro
            return [
                "O que poderíamos fazer para você nos recomendar com nota 10?",
                "Qual aspecto podemos melhorar?"
            ]
        else:
            # Detrator
            return [
                "Sentimos muito. O que aconteceu?",
                "Como podemos recuperar sua confiança?"
            ]


if __name__ == "__main__":
    print("🧪 Testando Agente Gerador de Mensagem")
    print("=" * 60)
    
    from agents.context_collector import ContextCollectorAgent
    from agents.sentiment_analyzer import SentimentAnalyzerAgent
    
    # Coletar e analisar contexto
    collector = ContextCollectorAgent()
    context = collector.collect("101")
    
    analyzer = SentimentAnalyzerAgent()
    analysis = analyzer.analyze(context)
    
    # Gerar mensagem
    generator = MessageGeneratorAgent()
    message = generator.generate(context, analysis)
    
    print("\n📧 Mensagem Gerada:")
    print(f"Tipo: {message['tipo']}")
    print(f"Tom: {message['tom']}")
    print(f"Assunto: {message['assunto']}")
    print("\n" + "="*60)
    print(message['mensagem'])
    print("="*60)
    
    # Mostrar pergunta NPS
    print("\n❓ Pergunta NPS:")
    print(generator.generate_nps_question())
    
    # Mostrar follow-up para nota 8
    print("\n📝 Perguntas de Follow-up (Nota 8 - Neutro):")
    for i, q in enumerate(generator.generate_follow_up_questions(8), 1):
        print(f"{i}. {q}")
