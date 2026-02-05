"""
NPS Multi-Agent API - Pareto Case
API FastAPI para expor o sistema multi-agente NPS
"""

import sys
import traceback
import os

# Remover path absoluto para compatibilidade com Vercel
# sys.path.append('/Users/julianamoraesferreira/Documents/Projetos-Dev-Petrick/pareto-case/langchain')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from agents.context_collector import ContextCollectorAgent
from agents.sentiment_analyzer import SentimentAnalyzerAgent
from agents.message_generator import MessageGeneratorAgent
from agents.response_evaluator import ResponseEvaluatorAgent
from agents.empathetic_response import EmpatheticResponseGenerator
from hubspot_client import HubSpotClient
from telegram_client import TelegramClient
from fastapi import Request, Header
from langsmith import traceable
from supabase_client import supabase_client

# Criar aplicação FastAPI
app = FastAPI(
    title="NPS Multi-Agent API - Pareto Case",
    description="API para orquestrar agentes de NPS com Tess AI e HubSpot Mock",
    version="1.0.0"
)

# Configurar CORS para permitir chamadas do N8N
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agentes
context_collector = ContextCollectorAgent()
sentiment_analyzer = SentimentAnalyzerAgent()
message_generator = MessageGeneratorAgent()
response_evaluator = ResponseEvaluatorAgent()
empathetic_generator = EmpatheticResponseGenerator()
empathetic_generator = EmpatheticResponseGenerator()
hubspot_client = HubSpotClient()
telegram_client = TelegramClient()

# Modelos Pydantic
class EvaluateRequest(BaseModel):
    score: int
    feedback: Optional[str] = ""
    contact_id: Optional[str] = None

class EvaluateResponse(BaseModel):
    nps_score: int
    classificacao: Dict[str, Any]
    prioridade: str
    insights: Dict[str, Any]
    acoes_recomendadas: list
    resumo_executivo: str
    resposta_empatica: str  # Nova: resposta humanizada para o cliente


class ManualMessageRequest(BaseModel):
    chat_id: str
    message: str
    manager_id: Optional[str] = None


class ManualModeRequest(BaseModel):
    chat_id: str
    manager_id: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check da API"""
    return {"status": "ok", "service": "nps-agent-api"}


@app.get("/contacts")
async def list_contacts():
    """Lista os contact_ids disponíveis no mock"""
    try:
        # Contact IDs fixos do mock
        contacts = [
            {
                "id": "101",
                "nome": "Cliente 1 (Elegível)",
                "descricao": "Tag mock_csat_survey=true, artefatos recentes",
                "perfil": "Participa do fluxo NPS"
            },
            {
                "id": "102", 
                "nome": "Cliente 2 (Elegível)",
                "descricao": "Tag mock_csat_survey=true, artefatos recentes",
                "perfil": "Participa do fluxo NPS"
            },
            {
                "id": "103",
                "nome": "Cliente 3 (Grupo Controle)",
                "descricao": "Sem tag CSAT, artefatos antigos",
                "perfil": "Não deve aparecer em filtros recentes"
            }
        ]
        
        return {
            "total": len(contacts),
            "contacts": contacts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contatos: {str(e)}")


@app.post("/nps/context/{contact_id}")
async def get_context(contact_id: str):
    """Executa apenas o ContextCollector para um contato"""
    try:
        print(f"DEBUG contact_id recebido: {contact_id}, tipo: {type(contact_id)}")
        print(f"🔍 Coletando contexto para contato {contact_id}...")
        context = context_collector.collect(contact_id, days_back=30)
        
        if not context:
            raise HTTPException(status_code=404, detail=f"Contato {contact_id} não encontrado ou erro na coleta")
        
        return {
            "contact_id": contact_id,
            "status": "success",
            "data": context
        }
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print("=" * 60)
        print("TRACEBACK COMPLETO:")
        print(error_trace)
        print("=" * 60)
        raise HTTPException(status_code=500, detail=f"Erro ao coletar contexto: {str(e)}")


@app.post("/nps/analyze/{contact_id}")
async def analyze_contact(contact_id: str):
    """Executa ContextCollector + SentimentAnalyzer"""
    try:
        print(f"🔍 Analisando contato {contact_id}...")
        
        # Etapa 1: Coletar contexto
        context = context_collector.collect(contact_id, days_back=30)
        if not context:
            raise HTTPException(status_code=404, detail=f"Contato {contact_id} não encontrado")
        
        # Etapa 2: Analisar sentimento
        analysis = sentiment_analyzer.analyze(context)
        
        return {
            "contact_id": contact_id,
            "status": "success",
            "contexto": context,
            "analise": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.post("/nps/generate-message/{contact_id}")
async def generate_nps_message(contact_id: str):
    """Executa fluxo completo até gerar mensagem NPS"""
    try:
        print(f"✉️ Gerando mensagem NPS para contato {contact_id}...")
        
        # Etapa 1: Coletar contexto
        context = context_collector.collect(contact_id, days_back=30)
        if not context:
            raise HTTPException(status_code=404, detail=f"Contato {contact_id} não encontrado")
        
        # Etapa 2: Analisar sentimento
        analysis = sentiment_analyzer.analyze(context)
        
        # Etapa 3: Gerar mensagem
        message = message_generator.generate(context, analysis)
        
        return {
            "contact_id": contact_id,
            "status": "success",
            "contexto": context,
            "analise": analysis,
            "mensagem_nps": message
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mensagem: {str(e)}")


@app.post("/nps/evaluate", response_model=EvaluateResponse)
async def evaluate_nps_response(request: EvaluateRequest):
    """Avalia uma resposta de NPS"""
    try:
        print(f"📊 Avaliando resposta NPS: {request.score}/10...")
        
        result = response_evaluator.evaluate(
            nps_score=request.score,
            feedback_text=request.feedback,
            context=None
        )
        
        # Gerar resposta empática para o cliente
        empathetic_response = empathetic_generator.generate_response(
            score=request.score,
            feedback_text=request.feedback
        )
        
        return EvaluateResponse(
            nps_score=result["nps_score"],
            classificacao=result["classificacao"],
            prioridade=result["prioridade"],
            insights=result["insights"],
            acoes_recomendadas=result["acoes_recomendadas"],
            resumo_executivo=result["resumo_executivo"],
            resposta_empatica=empathetic_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na avaliação: {str(e)}")


@app.post("/nps/full-flow/{contact_id}")
async def run_full_nps_flow(contact_id: str):
    """Executa run_nps_flow() completo consolidado"""
    try:
        print(f"🚀 Executando fluxo NPS completo para contato {contact_id}...")
        
        # Etapa 1: Coletar contexto
        context = context_collector.collect(contact_id, days_back=30)
        if not context:
            raise HTTPException(status_code=404, detail=f"Contato {contact_id} não encontrado")
        
        # Etapa 2: Analisar sentimento
        analysis = sentiment_analyzer.analyze(context)
        
        # Etapa 3: Gerar mensagem
        message = message_generator.generate(context, analysis)
        
        # Resumo consolidado - proteção para listas
        cliente = context.get("cliente", {}) if isinstance(context.get("cliente"), dict) else {}
        metricas = context.get("metricas", {}) if isinstance(context.get("metricas"), dict) else {}
        
        return {
            "contact_id": contact_id,
            "status": "success",
            "resumo_cliente": {
                "nome": cliente.get("nome"),
                "email": cliente.get("email"),
                "tempo_como_cliente": cliente.get("tempo_como_cliente"),
                "valor_total": metricas.get("valor_total"),
                "quantidade_deals": metricas.get("quantidade_deals"),
                "quantidade_tickets": metricas.get("quantidade_tickets"),
                "riscos_identificados": metricas.get("riscos_identificados")
            },
            "analise_sentimento": {
                "sentimento_geral": analysis.get("sentimento_geral"),
                "nivel_satisfacao": analysis.get("nivel_satisfacao"),
                "risco_churn": analysis.get("risco_churn"),
                "justificativa": analysis.get("justificativa"),
                "recomendacao": analysis.get("recomendacao")
            },
            "mensagem_nps": {
                "tom": message.get("tom"),
                "assunto": message.get("assunto"),
                "mensagem_completa": message.get("mensagem")
            },
            "proximos_passos": {
                "acao_recomendada": "Enviar mensagem NPS personalizada",
                "monitorar_resposta": True,
                "follow_up_automatico": analysis.get("risco_churn") in ["ALTO", "MEDIO"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no fluxo completo: {str(e)}")


@app.post("/telegram/send-manual")
async def send_manual_message(request: ManualMessageRequest):
    """Permite gestor enviar mensagem manual e pausar automação"""
    from conversation_manager import conversation_manager

    if not request.chat_id or not request.message.strip():
        raise HTTPException(status_code=400, detail="chat_id e message são obrigatórios")

    try:
        conversation_manager.enable_manual_mode(request.chat_id)

        # Enviar mensagem via Telegram
        sent = await telegram_client.send_message(int(request.chat_id), request.message.strip())
        if not sent:
            raise HTTPException(status_code=500, detail="Falha ao enviar mensagem manual")

        # Logar mensagem no Supabase
        session = conversation_manager.get_session(request.chat_id)
        supabase_client.log_conversation_message(
            chat_id=request.chat_id,
            message_text=request.message.strip(),
            sender="manager",
            conversation_state=session.state.value,
            nps_score=session.nps_score,
            sentiment=session.sentiment,
            metadata={
                "manager_id": request.manager_id,
                "manual_mode": True
            }
        )

        return {"status": "sent"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem manual: {str(e)}")


@app.post("/telegram/manual/enable")
async def enable_manual_mode(request: ManualModeRequest):
    """Ativa o modo manual para um chat específico"""
    from conversation_manager import conversation_manager

    if not request.chat_id:
        raise HTTPException(status_code=400, detail="chat_id é obrigatório")

    conversation_manager.enable_manual_mode(request.chat_id)
    session = conversation_manager.get_session(request.chat_id)
    supabase_client.log_conversation_message(
        chat_id=request.chat_id,
        message_text="[MANUAL_MODE] ativado",
        sender="system",
        conversation_state=session.state.value,
        nps_score=session.nps_score,
        sentiment=session.sentiment,
        metadata={"manager_id": request.manager_id, "manual_mode": True}
    )
    return {"status": "manual_enabled"}


@app.post("/telegram/manual/disable")
async def disable_manual_mode(request: ManualModeRequest):
    """Desativa o modo manual para um chat específico"""
    from conversation_manager import conversation_manager

    if not request.chat_id:
        raise HTTPException(status_code=400, detail="chat_id é obrigatório")

    conversation_manager.disable_manual_mode(request.chat_id)
    session = conversation_manager.get_session(request.chat_id)
    supabase_client.log_conversation_message(
        chat_id=request.chat_id,
        message_text="[MANUAL_MODE] desativado",
        sender="system",
        conversation_state=session.state.value,
        nps_score=session.nps_score,
        sentiment=session.sentiment,
        metadata={"manager_id": request.manager_id, "manual_mode": False}
    )
    return {"status": "manual_disabled"}


@app.post("/telegram/webhook")
@traceable(name="Telegram Webhook Handler")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    """Recebe updates do Telegram e processa via ConversationManager"""
    # 1. Validar Token Secreto (Segurança)
    expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        data = await request.json()
        message = data.get("message", {})
        
        if not message:
            return {"status": "ignored", "reason": "no_message"}
            
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not chat_id or not text:
            return {"status": "ignored", "reason": "no_text"}

        print(f"📩 Telegram Message de {chat_id}: {text}")
        
        # 2. Usar ConversationManager para processar mensagem
        from conversation_manager import conversation_manager
        
        response_text = await conversation_manager.process_message(
            chat_id=str(chat_id),
            text=text
        )
        
        # 3. Enviar resposta (se houver)
        if response_text:
            await telegram_client.send_message(chat_id, response_text)
            print(f"✅ Resposta enviada para {chat_id}")
        else:
            print(f"⏸️ Sem resposta (modo manual ou outro motivo)")
        
        return {"status": "processed"}
        
    except Exception as e:
        print(f"❌ Erro no Webhook Telegram: {e}")
        import traceback
        traceback.print_exc()
        # Não retornar erro 500 para o Telegram não ficar tentando re-entregar
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("🚀 Iniciando NPS Multi-Agent API - Pareto Case")
    print("=" * 60)
    print("📡 Endpoints disponíveis:")
    print("  • GET  /health")
    print("  • GET  /contacts")
    print("  • POST /nps/context/{contact_id}")
    print("  • POST /nps/analyze/{contact_id}")
    print("  • POST /nps/generate-message/{contact_id}")
    print("  • POST /nps/evaluate")
    print("  • POST /nps/full-flow/{contact_id}")
    print("=" * 60)
    print("🌐 Acesse: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
