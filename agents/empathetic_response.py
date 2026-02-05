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
        self.llm = TessLLM(temperature=0.7, max_tokens=200)
        
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
            prompt = f"""Você é a Tess, da Pareto.

CONTEXTO:
- Cliente: {nome}
- Score: {score}/10 ({categoria})
- Feedback: "{feedback_text}"

TAREFA:
Responda o {nome} de forma natural.

DIRETRIZES:
- Use o nome {nome}
- SEM EMOJIS (proibido)
- Curto e direto (máx 3 linhas)
- Não use frases prontas de call center
- Agradeça sinceramente

Resposta:"""
        else:
            # Versão SEM nome
            prompt = f"""Você é a Tess, da Pareto.

CONTEXTO:
- Score: {score}/10 ({categoria})
- Feedback: "{feedback_text}"

TAREFA:
Agradeça a avaliação de forma natural.

DIRETRIZES:
- SEM EMOJIS (proibido)
- Curto e direto (máx 3 linhas)
- Não use frases prontas de call center

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
    
    def _fallback_response(self, score: int, feedback_text: str, nome: str = "") -> str:
        """
        Resposta inteligente baseada em análise do feedback
        Mais sofisticada que templates fixos
        """
        
        # Analisar se tem feedback textual
        has_feedback = bool(feedback_text and len(feedback_text.strip()) > 3)
        name_part = f", {nome}" if nome else ""
        snippet = feedback_text.strip() if feedback_text else ""
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        snippet_text = f' Você comentou "{snippet}".' if snippet else ""
        
        if score <= 6:  # DETRATOR
            if has_feedback:
                return f"Sinto muito{name_part} pela experiência.{snippet_text} Pode me contar mais detalhes para eu ajudar?"
            return f"Sinto muito{name_part} pela experiência. Pode me dizer o que aconteceu? Isso vai nos ajudar a melhorar."
        
        if score <= 8:  # NEUTRO
            if has_feedback:
                return f"Obrigado{name_part} pelo feedback.{snippet_text} O que faltou para ficar excelente?"
            return f"Obrigado{name_part} pela avaliação. O que faltou para ser uma experiência ótima?"
        
        # PROMOTOR
        if has_feedback:
            return f"Que bom saber disso{name_part}!{snippet_text} O que você mais gostou?"
        return f"Que bom saber disso{name_part}. Obrigado pela confiança!"
    
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
