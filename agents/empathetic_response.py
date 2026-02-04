"""
Gerador de Respostas Empáticas Inteligentes para NPS
Usa TessLLM para criar respostas personalizadas baseadas no feedback do cliente
"""

from typing import Optional, Dict, Any, List
import os
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.llm.tess_llm import TessLLM
from langchain_core.prompts import PromptTemplate
from langsmith import traceable


class EmpatheticResponseGenerator:
    """Gera respostas empáticas INTELIGENTES usando Tess AI"""
    
    def __init__(self):
        """Inicializa o gerador com TessLLM"""
        self.llm = TessLLM(temperature=0.9, max_tokens=250)
        
        # Prompt template para respostas empáticas
        self.prompt_template = PromptTemplate(
            input_variables=["score", "categoria", "feedback", "sentimento", "contexto"],
            template="""Você é a Tess, assistente empática da Pareto, especializada em atendimento ao cliente.

CONTEXTO DA AVALIAÇÃO:
- Score NPS: {score}/10
- Categoria: {categoria}
- Sentimento detectado: {sentimento}
- Feedback do cliente: "{feedback}"
{contexto}

TAREFA:
Escreva uma resposta NATURAL, EMPÁTICA e PERSONALIZADA para o cliente.

DIRETRIZES:
- Seja genuína e humana, não robótica
- Reconheça especificamente o que o cliente mencionou
- Use tom conversacional e profissional
- SEM EMOJIS
- Seja breve (máximo 3-4 linhas)
- Se score baixo: mostre empatia e vontade de resolver
- Se score médio: agradeça e pergunte como melhorar
- Se score alto: celebre e agradeça

IMPORTANTE:
- NÃO use frases corporativas genéricas
- NÃO repita exatamente o que o cliente disse
- Responda como se fosse uma pessoa real conversando
- Sempre se identifique como "Tess" se necessário

Resposta:"""
        )
    
    @traceable(name="Empathetic Response Generation")
    def generate_response(
        self, 
        score: int, 
        feedback_text: str = "",
        conversation_history: List[Dict] = None,
        sentiment: Dict[str, Any] = None,
        cliente_dados: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Gera resposta empática INTELIGENTE baseada na nota E no feedback
        
        Args:
            score: Nota NPS (0-10)
            feedback_text: Feedback textual do cliente
            conversation_history: Histórico de mensagens (opcional)
            sentiment: Resultado da análise de sentimento (opcional)
            cliente_dados: Dados do cliente do HubSpot (opcional)
            
        Returns:
            Mensagem empática personalizada e contextualizada
        """
        
        # Determinar categoria NPS
        if score <= 6:
            categoria = "DETRATOR"
        elif score <= 8:
            categoria = "NEUTRO"
        else:
            categoria = "PROMOTOR"
        
        # Extrair sentimento
        sentimento_str = "NEUTRO"
        if sentiment:
            sentimento_str = sentiment.get("sentimento", "NEUTRO")
        
        # Preparar contexto do cliente
        contexto_cliente = ""
        nome = ""
        
        if cliente_dados:
            props = cliente_dados.get("properties", {})
            nome = props.get("firstname", "")
            
            if nome:
                contexto_cliente = f"\n- Nome do cliente: {nome}"
        
        # Construir prompt personalizado
        if nome:
            # Versão COM nome
            prompt = f"""Você é a Tess, assistente empática da Pareto.

CONTEXTO DA AVALIAÇÃO:
- Cliente: {nome}
- Score NPS: {score}/10
- Categoria: {categoria}
- Sentimento: {sentimento_str}
- Feedback: "{feedback_text}"

TAREFA:
Escreva uma resposta NATURAL e EMPÁTICA para {nome}.

DIRETRIZES:
- Use o nome {nome} na resposta
- Seja genuína e humana
- SEM EMOJIS
- Máximo 3-4 linhas

DETRATOR (0-6): Acolha e peça desculpas
NEUTRO (7-8): Agradeça e pergunte como melhorar
PROMOTOR (9-10): Celebre e agradeça

Resposta:"""
        else:
            # Versão SEM nome
            prompt = f"""Você é a Tess, assistente empática da Pareto.

CONTEXTO DA AVALIAÇÃO:
- Score NPS: {score}/10
- Categoria: {categoria}
- Sentimento: {sentimento_str}
- Feedback: "{feedback_text}"

TAREFA:
Escreva uma resposta NATURAL e EMPÁTICA.

DIRETRIZES:
- Seja genuína e humana
- SEM EMOJIS
- Máximo 3-4 linhas

DETRATOR (0-6): Acolha e peça desculpas
NEUTRO (7-8): Agradeça e pergunte como melhorar
PROMOTOR (9-10): Celebre e agradeça

Resposta:"""
        
        try:
            # Gerar resposta com TessLLM
            response = self.llm.invoke(prompt)
            
            print(f"✅ Resposta empática gerada via TessLLM (score: {score}, categoria: {categoria})")
            return response.strip()
            
        except Exception as e:
            print(f"❌ Erro ao gerar resposta empática: {e}")
            # Fallback para resposta básica
            return self._fallback_response(score, feedback_text, nome)
    
    def _fallback_response(self, score: int, feedback: str, nome: str = "") -> str:
        """
        Resposta inteligente baseada em análise do feedback
        Mais sofisticada que templates fixos
        """
        
        # Analisar se tem feedback textual
        has_feedback = bool(feedback_text and len(feedback_text.strip()) > 3)
        
        if score <= 6:  # DETRATOR
            if has_feedback:
                # Analisar palavras-chave no feedback
                feedback_lower = feedback_text.lower()
                
                if any(word in feedback_lower for word in ['atendimento', 'suporte', 'resposta', 'contato']):
                    return f"Poxa, que situação chata com o atendimento. 😔 Você mencionou '{feedback_text[:50]}...' - pode me contar mais detalhes sobre o que aconteceu? Queremos muito corrigir isso."
                
                elif any(word in feedback_lower for word in ['produto', 'qualidade', 'funciona', 'bug', 'erro']):
                    return f"Entendo sua frustração com o produto. 😔 Sobre '{feedback_text[:50]}...' - isso não deveria acontecer. Pode me explicar melhor para eu escalar pro time técnico?"
                
                elif any(word in feedback_lower for word in ['preço', 'caro', 'valor', 'custo']):
                    return f"Entendo sua preocupação com o valor. Sobre '{feedback_text[:50]}...' - queremos entender melhor sua percepção. Pode me contar mais?"
                
                else:
                    return f"Poxa, sentimos muito. 😔 Vi que você mencionou '{feedback_text[:50]}...' - pode me contar mais detalhes? Queremos muito melhorar isso."
            
            else:
                return "Opa, vi que você deu uma nota baixa. 😔 Rolou algum problema específico? Conta pra gente, queremos muito entender e melhorar."
        
        elif score <= 8:  # NEUTRO
            if has_feedback:
                feedback_lower = feedback_text.lower()
                
                if any(word in feedback_lower for word in ['ok', 'normal', 'médio', 'razoável']):
                    return f"Legal que tá funcionando! Mas vi que você disse '{feedback_text[:50]}...' - o que falta para ser perfeito? Pode ser bem sincero!"
                
                elif any(word in feedback_lower for word in ['poderia', 'falta', 'melhorar', 'gostaria']):
                    return f"Obrigado pelo feedback! Sobre '{feedback_text[:50]}...' - adoraríamos ouvir mais sugestões. O que mais poderíamos fazer?"
                
                else:
                    return f"Obrigado! Vi que você mencionou '{feedback_text[:50]}...' - tem mais alguma coisa que poderíamos melhorar? Sua opinião é muito valiosa!"
            
            else:
                return "Obrigado pelo feedback! O que falta para ser perfeito pra você? Pode ser sincero, vai nos ajudar muito! 💙"
        
        else:  # PROMOTOR
            if has_feedback:
                feedback_lower = feedback_text.lower()
                
                if any(word in feedback_lower for word in ['adorei', 'amei', 'excelente', 'perfeito', 'ótimo']):
                    return f"Que alegria ouvir isso! 🤩 Sobre '{feedback_text[:50]}...' - fico super feliz que você curtiu! Quer contar mais sobre o que te surpreendeu?"
                
                elif any(word in feedback_lower for word in ['equipe', 'atendimento', 'time', 'pessoal']):
                    return f"Que feedback incrível! 🤩 A equipe vai adorar saber sobre '{feedback_text[:50]}...' - tem mais algum detalhe que você queira compartilhar?"
                
                else:
                    return f"Muito obrigado! 🤩 Adoramos saber sobre '{feedback_text[:50]}...' - quer contar mais sobre o que você mais gostou?"
            
            else:
                return "Que alegria saber disso! 🤩 Muito obrigado pela confiança. Se quiser compartilhar o que você mais gostou, ficaremos felizes em ouvir!"
    
    @staticmethod
    def generate_follow_up_question(score: int) -> str:
        """Gera pergunta de follow-up baseada na nota"""
        
        if score <= 6:
            return "O que aconteceu que te deixou insatisfeito(a)?"
        elif score <= 8:
            return "O que falta para sua experiência ser perfeita?"
        else:
            return "O que você mais gostou na nossa parceria?"


if __name__ == "__main__":
    # Testes
    generator = EmpatheticResponseGenerator()
    
    print("🧪 Testando Respostas Inteligentes\n")
    
    test_cases = [
        (3, "O atendimento foi horrível, ninguém me respondeu"),
        (2, "O produto não funciona, cheio de bugs"),
        (5, "Muito caro para o que oferece"),
        (7, "Tá ok, mas poderia ser melhor"),
        (8, "Normal, nada de especial"),
        (10, "Adorei tudo! Vocês são incríveis!"),
        (9, "A equipe de suporte é excelente"),
        (5, ""),  # Sem feedback
    ]
    
    for score, feedback in test_cases:
        print(f"Score: {score}/10")
        print(f"Feedback: '{feedback}'")
        print(f"Resposta: {generator.generate_response(score, feedback)}")
        print("-" * 80)
