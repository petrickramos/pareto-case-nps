"""
Agente Gerador de Mensagem
Responsável por criar mensagens personalizadas de pesquisa NPS
"""

from typing import Dict, Any
from tess_client import TessClient


class MessageGeneratorAgent:
    def __init__(self):
        self.tess = TessClient()
        self.agent_id = "message-generator"  # Placeholder
    
    def generate(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera mensagem personalizada de pesquisa NPS
        
        Args:
            context: Contexto do cliente
            analysis: Análise de sentimento e riscos
            
        Returns:
            Dict com mensagem completa e metadata
        """
        print("✍️ Gerando mensagem personalizada de NPS...")
        
        cliente = context.get("cliente", {})
        sentimento = analysis.get("sentimento_geral", "NEUTRO")
        risco = analysis.get("risco_churn", "MEDIO")
        
        # Escolher estratégia baseada no perfil
        if risco == "ALTO" or sentimento == "NEGATIVO":
            mensagem = self._generate_careful_message(context, analysis)
        elif sentimento == "POSITIVO":
            mensagem = self._generate_enthusiastic_message(context, analysis)
        else:
            mensagem = self._generate_standard_message(context, analysis)
        
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
        
        print(f"✅ Mensagem gerada: Tom {result['tom']}")
        
        return result
    
    def _generate_careful_message(self, context: Dict, analysis: Dict) -> str:
        """Mensagem para clientes com risco/cautelosos"""
        
        cliente = context.get("cliente", {})
        nome = cliente.get("nome", "Cliente").split()[0]  # Primeiro nome
        
        mensagem = f"""Olá {nome},

Esperamos que esteja bem. Notamos que você teve algumas interações recentes conosco e queremos garantir que sua experiência tenha sido a melhor possível.

Sua opinião é muito importante para continuarmos melhorando. Poderia dedicar 1 minuto para nos contar como foi sua experiência?

Acesse a pesquisa aqui: [LINK_PESQUISA]

Agradecemos sua paciência e confiança em nossa parceria.

Atenciosamente,
Equipe Pareto"""
        
        return mensagem
    
    def _generate_enthusiastic_message(self, context: Dict, analysis: Dict) -> str:
        """Mensagem para clientes satisfeitos/engajados"""
        
        cliente = context.get("cliente", {})
        metricas = context.get("metricas", {})
        nome = cliente.get("nome", "Cliente").split()[0]
        
        # Personalizar se for cliente de alto valor
        valor = metricas.get("valor_total", 0)
        tempo = cliente.get("tempo_como_cliente", "")
        
        mensagem = f"""Olá {nome},

Você é um cliente {valor > 20000 and 'valioso' or 'importante'} para nós! {tempo and f'Há {tempo}' or 'Há algum tempo'} você confia em nossa parceria e isso significa muito.

Gostaríamos de ouvir sua opinião sobre como podemos ser ainda melhores. Sua experiência e feedback nos ajudam a evoluir constantemente.

Responda nossa pesquisa rápida (só 1 minuto): [LINK_PESQUISA]

Agradecemos por fazer parte da nossa história!

Um abraço,
Equipe Pareto"""
        
        return mensagem
    
    def _generate_standard_message(self, context: Dict, analysis: Dict) -> str:
        """Mensagem padrão para clientes neutros"""
        
        cliente = context.get("cliente", {})
        nome = cliente.get("nome", "Cliente").split()[0]
        
        mensagem = f"""Olá {nome},

Como parte do nosso compromisso contínuo com a excelência, gostaríamos de ouvir sua opinião sobre nossos serviços.

Sua avaliação nos ajuda a identificar o que estamos fazendo bem e onde podemos melhorar.

Poderia responder nossa pesquisa rápida? Leva apenas 1 minuto: [LINK_PESQUISA]

Agradecemos sua participação!

Atenciosamente,
Equipe Pareto"""
        
        return mensagem
    
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
