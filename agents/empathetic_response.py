"""
Gerador de Respostas Empáticas Inteligentes para NPS
Usa TessClient para criar respostas personalizadas baseadas no feedback do cliente
"""

from typing import Optional
import os
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tess_client import TessClient


class EmpatheticResponseGenerator:
    """Gera respostas empáticas INTELIGENTES baseadas no feedback do cliente"""
    
    def __init__(self):
        """Inicializa o gerador com TessClient"""
        self.client = TessClient()
        # ID do agente de geração de mensagens (você pode criar um agente específico na Tess)
        self.agent_id = os.getenv("TESS_EMPATHY_AGENT_ID", "default")
    
    def generate_response(self, score: int, feedback_text: str = "") -> str:
        """
        Gera resposta empática INTELIGENTE baseada na nota E no feedback
        
        Args:
            score: Nota NPS (0-10)
            feedback_text: Feedback textual do cliente
            
        Returns:
            Mensagem empática personalizada e contextualizada
        """
        
        # Classificar categoria
        if score <= 6:
            categoria = "DETRATOR"
        elif score <= 8:
            categoria = "NEUTRO"
        else:
            categoria = "PROMOTOR"
        
        # Por enquanto, usar fallback inteligente baseado no feedback
        # TODO: Quando tiver agente específico na Tess, usar execute_agent
        return self._intelligent_fallback(score, categoria, feedback_text)
    
    def _intelligent_fallback(self, score: int, categoria: str, feedback_text: str) -> str:
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
