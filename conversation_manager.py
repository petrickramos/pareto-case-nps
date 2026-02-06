"""
Conversation Manager - Gerenciador de Estado de Conversas NPS
Responsável por orquestrar agentes e manter contexto de conversação
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import re
from langsmith import traceable

from agents.sentiment_analyzer import SentimentAnalyzerAgent
from agents.empathetic_response import EmpatheticResponseGenerator
from agents.response_evaluator import ResponseEvaluatorAgent
from services.cliente_service import cliente_service
from supabase_client import supabase_client


START_REQUIRED_MESSAGE = "Para começar, digite /start."
GREETING_BASE_MESSAGE = (
    "Olá{nome}! Tudo bem?\n\n"
    "Sou a Tess, assistente de qualidade da Pareto.\n\n"
    "Gostaríamos muito de saber como foi a sua experiência conosco, "
    "posso te dar mais detalhes sobre como deixar seu feedback?"
)
ASK_SCORE_MESSAGE = (
    "Maravilha! Por favor, atribua uma nota de 0 a 10 sobre a sua "
    "experiência usando a Tess."
)
DETAILS_MESSAGE = (
    "Entendi, basta digitar no teclado do celular mesmo uma nota de 0 a 10 "
    "sobre a sua experiência usando a Tess."
)
DECLINE_MESSAGE = (
    "Sem problemas! Quando quiser participar, é só digitar /start novamente."
)
CONFIRMATION_FALLBACK_MESSAGE = (
    "Você gostaria de deixar seu feedback agora? Responda sim ou não."
)


class ConversationState(Enum):
    """Estados possíveis de uma conversa NPS"""
    IDLE = "idle"                        # Aguardando início
    WAITING_CONFIRMATION = "waiting_confirmation"  # Aguardando confirmação do usuário
    WAITING_SCORE = "waiting_score"      # Aguardando nota NPS (0-10)
    WAITING_FEEDBACK = "waiting_feedback"  # Aguardando justificativa textual
    COMPLETED = "completed"              # Conversa finalizada
    MANUAL_MODE = "manual_mode"          # Gerente assumiu controle


class ConversationSession:
    """Representa uma sessão de conversa com um usuário"""
    
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.state = ConversationState.IDLE
        self.nps_score: Optional[int] = None
        self.feedback_text: str = ""
        self.sentiment: Optional[str] = None
        self.messages_history: list = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.manual_mode = False
        
        # NOVO: Dados do cliente (HubSpot Mock)
        self.cliente_identificado: bool = False
        self.dados_cliente: Optional[Dict[str, Any]] = None

    def reset_for_new_conversation(self):
        """Reseta campos da sessão para iniciar nova conversa"""
        self.state = ConversationState.IDLE
        self.nps_score = None
        self.feedback_text = ""
        self.sentiment = None
        self.messages_history = []
        self.updated_at = datetime.now()
        self.manual_mode = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa sessão para dict"""
        return {
            "chat_id": self.chat_id,
            "state": self.state.value,
            "nps_score": self.nps_score,
            "feedback_text": self.feedback_text,
            "sentiment": self.sentiment,
            "messages_count": len(self.messages_history),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "manual_mode": self.manual_mode,
            "cliente_identificado": self.cliente_identificado,
            "cliente_nome": self.dados_cliente.get("firstname") if self.dados_cliente else None
        }


class ConversationManager:
    """
    Gerenciador de conversas NPS com máquina de estados
    Orquestra múltiplos agentes para criar experiência inteligente
    """
    
    def __init__(self):
        # Cache de sessões em memória (em produção, usar Redis)
        self.sessions: Dict[str, ConversationSession] = {}
        
        # Inicializar agentes
        self.sentiment_analyzer = SentimentAnalyzerAgent()
        self.empathetic_generator = EmpatheticResponseGenerator()
        self.response_evaluator = ResponseEvaluatorAgent()
        
        # Serviço de clientes
        self.cliente_service = cliente_service

    
    def get_session(self, chat_id: str) -> ConversationSession:
        """Recupera ou cria uma sessão de conversa"""
        if chat_id not in self.sessions:
            self.sessions[chat_id] = ConversationSession(chat_id)
            print(f"🆕 Nova sessão criada para chat_id: {chat_id}")
        return self.sessions[chat_id]
    
    def transition_state(self, chat_id: str, new_state: ConversationState):
        """Transição de estado com logging"""
        session = self.get_session(chat_id)
        old_state = session.state
        session.state = new_state
        session.updated_at = datetime.now()
        
        print(f"🔄 Estado mudou: {old_state.value} → {new_state.value} (chat: {chat_id})")
        
        # Logar transição no Supabase
        supabase_client.log_conversation_message(
            chat_id=chat_id,
            message_text=f"[STATE_TRANSITION] {old_state.value} → {new_state.value}",
            sender="system",
            conversation_state=new_state.value,
            metadata={"transition": True}
        )
    
    @traceable(name="Process User Message")
    async def process_message(self, chat_id: str, text: str, username: Optional[str] = None) -> str:
        """
        Processa mensagem do usuário baseado no estado atual
        Retorna resposta inteligente do bot
        """
        session = self.get_session(chat_id)
        
        # Adicionar mensagem ao histórico
        session.messages_history.append({
            "sender": "user",
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Logar mensagem do usuário no Supabase
        supabase_client.log_conversation_message(
            chat_id=chat_id,
            message_text=text,
            sender="user",
            conversation_state=session.state.value,
            nps_score=session.nps_score,
            sentiment=session.sentiment
        )

        # Se estiver em modo manual, apenas registrar (sem responder automaticamente)
        if session.manual_mode:
            return None

        if self._is_start_command(text):
            self._reset_session_for_start(chat_id, session)
        
        # Processar baseado no estado
        if session.state == ConversationState.IDLE:
            response = await self._handle_idle(chat_id, text, username)  # Passar username

        elif session.state == ConversationState.WAITING_CONFIRMATION:
            response = await self._handle_waiting_confirmation(chat_id, text)
        
        elif session.state == ConversationState.WAITING_SCORE:
            response = await self._handle_waiting_score(chat_id, text)
        
        elif session.state == ConversationState.WAITING_FEEDBACK:
            response = await self._handle_waiting_feedback(chat_id, text)
        
        elif session.state == ConversationState.COMPLETED:
            response = await self._handle_completed(chat_id, text)
        
        else:
            response = "Desculpe, algo deu errado. Vamos recomeçar? Digite /start"
        
        # Adicionar resposta ao histórico
        if response:
            session.messages_history.append({
                "sender": "bot",
                "text": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Logar resposta do bot no Supabase
            supabase_client.log_conversation_message(
                chat_id=chat_id,
                message_text=response,
                sender="bot",
                conversation_state=session.state.value,
                nps_score=session.nps_score,
                sentiment=session.sentiment
            )
        
        return response
    
    async def _tentar_identificar_cliente(self, chat_id: str, username: Optional[str] = None) -> Optional[Dict]:
        """
        Tenta identificar cliente no HubSpot Mock
        
        Estratégia:
        1. Buscar no cache por chat_id
        2. Buscar no HubSpot por username (como email)
        3. Fallback: retornar None
        
        Args:
            chat_id: ID do chat Telegram
            username: Username do Telegram (opcional)
            
        Returns:
            Dados do cliente ou None
        """
        session = self.get_session(chat_id)
        
        # Já identificado?
        if session.cliente_identificado:
            return session.dados_cliente
        
        # Tentar buscar por chat_id no cache
        cliente = self.cliente_service.buscar_por_chat_id(chat_id)
        if cliente:
            print(f"✅ Cliente identificado por chat_id: {chat_id}")
            return cliente
        
        # Tentar buscar por username (assumir que é email)
        if username:
            # Tentar como email direto
            email = f"{username}@exemplo.com" if "@" not in username else username
            cliente = self.cliente_service.buscar_por_email(email)
            
            if cliente:
                print(f"✅ Cliente identificado por email: {email}")
                # Coletar contexto completo
                contact_id = cliente.get("id")
                if contact_id:
                    contexto = self.cliente_service.coletar_contexto(contact_id)
                    cliente["contexto"] = contexto
                
                return cliente
        
        print(f"⚠️ Cliente não identificado (chat_id: {chat_id}, username: {username})")
        return None
    
    async def _handle_idle(self, chat_id: str, text: str, username: Optional[str] = None) -> str:
        """Estado IDLE: Aguardando início da conversa (requer /start)"""
        
        session = self.get_session(chat_id)

        if not self._is_start_command(text):
            return START_REQUIRED_MESSAGE
        
        # Tentar identificar cliente (se ainda não identificado)
        if not session.cliente_identificado:
            cliente = await self._tentar_identificar_cliente(chat_id, username)
            if cliente:
                session.cliente_identificado = True
                session.dados_cliente = cliente
                print(f"✅ Cliente identificado: {cliente.get('properties', {}).get('firstname', 'N/A')}")
        
        self.transition_state(chat_id, ConversationState.WAITING_CONFIRMATION)
        return self._gerar_saudacao(session)

    async def _handle_waiting_confirmation(self, chat_id: str, text: str) -> str:
        """Estado WAITING_CONFIRMATION: Aguardando confirmação do usuário"""
        score = self._extract_score(text)
        if score is not None:
            self.transition_state(chat_id, ConversationState.WAITING_SCORE)
            return await self._handle_waiting_score(chat_id, text)

        intent = self._classify_confirmation_intent(text)

        if intent == "details":
            self.transition_state(chat_id, ConversationState.WAITING_SCORE)
            return DETAILS_MESSAGE

        if intent == "confirm":
            self.transition_state(chat_id, ConversationState.WAITING_SCORE)
            return ASK_SCORE_MESSAGE

        if intent == "decline":
            self.transition_state(chat_id, ConversationState.IDLE)
            return DECLINE_MESSAGE

        return CONFIRMATION_FALLBACK_MESSAGE
    
    def _gerar_saudacao(self, session: 'ConversationSession') -> str:
        """Gera saudação baseada no novo fluxo de confirmação"""
        nome = ""
        if session.cliente_identificado and session.dados_cliente:
            props = session.dados_cliente.get("properties", {})
            nome = props.get("firstname", "").strip()

        nome_suffix = f", {nome}" if nome else ""
        return GREETING_BASE_MESSAGE.format(nome=nome_suffix)
    
    @traceable(name="Extract NPS Score")
    async def _handle_waiting_score(self, chat_id: str, text: str) -> str:
        """Estado WAITING_SCORE: Extrair nota e feedback"""
        session = self.get_session(chat_id)
        
        # Tentar extrair nota (0-10)
        score = self._extract_score(text)
        
        if score is not None:
            session.nps_score = score
            session.feedback_text = text
            
            # Analisar sentimento do feedback
            sentiment_result = await self._analyze_sentiment(chat_id, text, score)
            session.sentiment = sentiment_result.get("sentimento_geral", "NEUTRO")
            
            # Gerar resposta empática usando IA
            response = await self._generate_empathetic_response(
                chat_id, score, text, sentiment_result
            )
            
            # Avaliar e registrar NPS
            await self._evaluate_and_log_nps(chat_id, score, text)
            
            # Transição para COMPLETED
            self.transition_state(chat_id, ConversationState.COMPLETED)
            
            return response
        else:
            # Não encontrou nota - usar IA para responder e pedir nota
            from agents.llm.tess_llm import TessLLM
            
            try:
                llm = TessLLM(temperature=0.8, max_tokens=150)
                prompt = f"""Você é a Tess, assistente da Pareto. Está coletando avaliação NPS.

Usuário disse: \"{text}\"

Você precisa de uma nota de 0 a 10, mas o usuário não deu.

Responda:
1. Primeiro, responda a mensagem deles de forma natural
2. Depois, peça a nota de 0 a 10

Diretrizes:
- Sem emojis
- Natural e conversacional
- Máximo 2-3 linhas

Resposta:"""
                response = llm.invoke(prompt)
                return response.strip()
            except:
                # Fallback
                return (
                    "Não consegui identificar uma nota de 0 a 10 na sua mensagem. "
                    "Pode me dizer quanto você nos daria? Por exemplo: "
                    "'Dou nota 8' ou simplesmente '8'."
                )
    
    async def _handle_waiting_feedback(self, chat_id: str, text: str) -> str:
        """Estado WAITING_FEEDBACK: Coletar justificativa adicional"""
        session = self.get_session(chat_id)
        
        # Adicionar feedback adicional
        session.feedback_text += f" {text}"
        
        # Gerar resposta de agradecimento
        response = "Muito obrigado pelo seu feedback detalhado! Vamos usar isso para melhorar nossos serviços."
        
        self.transition_state(chat_id, ConversationState.COMPLETED)
        return response
    
    async def _handle_completed(self, chat_id: str, text: str) -> str:
        """Estado COMPLETED: Conversa já finalizada"""
        
        return (
            "Obrigado! Sua avaliação já foi registrada.\n\n"
            "Se quiser fazer uma nova avaliação, digite /start novamente."
        )

    def _reset_session_for_start(self, chat_id: str, session: ConversationSession):
        """Reinicia a sessão para um novo /start"""
        if session.state != ConversationState.IDLE:
            self.transition_state(chat_id, ConversationState.IDLE)
        session.reset_for_new_conversation()

    def _is_start_command(self, text: str) -> bool:
        return text.strip().lower().startswith("/start")

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def _classify_confirmation_intent(self, text: str) -> str:
        """Classifica intenção do usuário após a saudação"""
        normalized = self._normalize_text(text)

        if not normalized:
            return "unknown"

        detail_phrases = [
            "como atribuo",
            "como faço",
            "como faco",
            "como fazer",
            "como funciona",
            "como deixo",
            "como dou",
            "como dar",
            "como avaliar",
            "como envio",
            "como mandar",
            "mais detalhes",
            "detalhes",
            "explica",
            "explicar",
            "o que é isso",
            "o que e isso",
        ]

        if any(phrase in normalized for phrase in detail_phrases):
            return "details"

        if "como" in normalized and re.search(
            r"\b(atribuir|atribuo|fa[cç]o|faco|faz|fazer|funciona|deixo|dar|nota|avaliar)\b",
            normalized
        ):
            return "details"

        if re.search(r"\b(sim|claro|ok|okay|certo|beleza|pode|pode ser|vamos|bora)\b", normalized):
            return "confirm"

        if re.search(r"\b(n[aã]o|nao)\b", normalized):
            return "decline"

        if any(
            phrase in normalized
            for phrase in ["prefiro não", "prefiro nao", "agora não", "agora nao", "depois"]
        ):
            return "decline"

        return "unknown"
    
    def _extract_score(self, text: str) -> Optional[int]:
        """Extrai nota NPS (0-10) do texto"""
        
        # Padrões para detectar nota
        patterns = [
            r'\b(10|[0-9])\s*(?:/\s*10)?\b',  # "8", "8/10"
            r'nota\s+(10|[0-9])\b',            # "nota 8"
            r'dou\s+(10|[0-9])\b',             # "dou 8"
            r'daria\s+(10|[0-9])\b',           # "daria 8"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                score = int(match.group(1))
                if 0 <= score <= 10:
                    return score
        
        return None
    
    @traceable(name="Sentiment Analysis")
    async def _analyze_sentiment(self, chat_id: str, text: str, score: int) -> Dict[str, Any]:
        """Analisa sentimento do feedback usando SentimentAnalyzer"""
        
        # Criar contexto mínimo para análise
        context = {
            "cliente": {"id": chat_id},
            "metricas": {"nps_score": score},
            "feedback": text
        }
        
        try:
            analysis = self.sentiment_analyzer.analyze(context)
            return analysis
        except Exception as e:
            print(f"⚠️ Erro na análise de sentimento: {e}")
            # Fallback simples
            if score <= 6:
                return {"sentimento_geral": "NEGATIVO", "nivel_satisfacao": score}
            elif score <= 8:
                return {"sentimento_geral": "NEUTRO", "nivel_satisfacao": score}
            else:
                return {"sentimento_geral": "POSITIVO", "nivel_satisfacao": score}
    
    @traceable(name="Generate Empathetic Response")
    async def _generate_empathetic_response(
        self, 
        chat_id: str, 
        score: int, 
        feedback: str,
        sentiment: Dict[str, Any]
    ) -> str:
        """Gera resposta empática usando TessLLM"""
        session = self.get_session(chat_id)
        
        try:
            # Usar gerador empático com contexto completo
            response = self.empathetic_generator.generate_response(
                score=score,
                feedback_text=feedback,
                conversation_history=session.messages_history,
                sentiment=sentiment,
                cliente_dados=session.dados_cliente  # NOVO: Passar dados do cliente
            )
            
            print(f"✅ Resposta empática gerada: {response[:50]}...")
            return response
        except Exception as e:
            print(f"⚠️ Erro ao gerar resposta empática: {e}")
            # Fallback
            return f"Obrigado pela sua avaliação! Registramos sua nota {score}/10."
    
    @traceable(name="NPS Evaluation")
    async def _evaluate_and_log_nps(self, chat_id: str, score: int, feedback: str):
        """Avalia e registra NPS no sistema"""
        
        try:
            evaluation = self.response_evaluator.evaluate(
                nps_score=score,
                feedback_text=feedback,
                context={"source": "telegram", "contact_id": chat_id}
            )
            
            print(f"✅ NPS registrado: {score}/10 - {evaluation.get('classificacao', {}).get('categoria')}")
            
        except Exception as e:
            print(f"⚠️ Erro ao avaliar NPS: {e}")
    
    def enable_manual_mode(self, chat_id: str):
        """Ativa modo manual (gerente assume controle)"""
        session = self.get_session(chat_id)
        session.manual_mode = True
        self.transition_state(chat_id, ConversationState.MANUAL_MODE)
        print(f"👤 Modo manual ativado para chat {chat_id}")
    
    def disable_manual_mode(self, chat_id: str):
        """Desativa modo manual (volta ao automático)"""
        session = self.get_session(chat_id)
        session.manual_mode = False
        # Voltar ao estado anterior ou IDLE
        self.transition_state(chat_id, ConversationState.IDLE)
        print(f"🤖 Modo automático restaurado para chat {chat_id}")


# Instância global (singleton)
conversation_manager = ConversationManager()
