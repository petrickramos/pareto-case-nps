"""
Gerador de Respostas Empáticas para NPS
Cria respostas humanas e personalizadas baseadas na nota do cliente
"""

from typing import Dict


class EmpatheticResponseGenerator:
    """Gera respostas empáticas baseadas na nota NPS"""
    
    @staticmethod
    def generate_response(score: int, feedback_text: str = "") -> str:
        """
        Gera resposta empática baseada na nota NPS
        
        Args:
            score: Nota NPS (0-10)
            feedback_text: Feedback textual do cliente (opcional)
            
        Returns:
            Mensagem empática personalizada
        """
        
        if score <= 6:
            # DETRATOR - Empatia e vontade de melhorar
            return """Poxa, sentimos muito por isso. 😔

Poderia nos contar um pouco mais sobre o que aconteceu? Queremos muito melhorar e sua opinião é super importante pra gente.

Se preferir, pode responder aqui mesmo ou pedir para falar com alguém da equipe."""
        
        elif score <= 8:
            # NEUTRO - Curiosidade e abertura
            return """Obrigado pelo feedback! 

O que poderíamos fazer para te surpreender da próxima vez? Adoraríamos ouvir suas sugestões. 💙

Qualquer detalhe que quiser compartilhar vai nos ajudar muito!"""
        
        else:
            # PROMOTOR - Gratidão e celebração
            return """Que alegria saber disso! 🤩

Muito obrigado pela confiança. Se quiser compartilhar mais detalhes do que você mais gostou, ficaremos felizes em ouvir!

Você faz parte da nossa história. 💙"""
    
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
    
    print("🧪 Testando Respostas Empáticas\n")
    
    for score in [3, 7, 10]:
        print(f"Score: {score}/10")
        print(generator.generate_response(score))
        print(f"Follow-up: {generator.generate_follow_up_question(score)}")
        print("-" * 60)
