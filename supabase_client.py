
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import traceback

# Load environment variables
load_dotenv()

class SupabaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("⚠️ AVISO: Credenciais Supabase não encontradas no .env")
            self.client = None
        else:
            try:
                self.client: Client = create_client(url, key)
                self._initialized = True
            except Exception as e:
                print(f"❌ Erro ao inicializar Supabase: {e}")
                self.client = None

    def log_interaction(self, contact_id, interaction_type, agent_name, 
                       input_data, output_data, success=True, 
                       error_message=None, processing_time_ms=0):
        """
        Registra uma interação no banco de dados.
        Safe-fail: Se o supabase não estiver configurado ou der erro, apenas loga no console.
        """
        if not self.client:
            return None
            
        try:
            data = {
                "contact_id": str(contact_id),
                "interaction_type": interaction_type,
                "agent_name": agent_name,
                "input_data": input_data if isinstance(input_data, dict) else {"raw": str(input_data)},
                "output_data": output_data if isinstance(output_data, dict) else {"raw": str(output_data)},
                "success": success,
                "error_message": str(error_message) if error_message else None,
                "processing_time_ms": int(processing_time_ms)
            }
            
            result = self.client.table("nps_interactions").insert(data).execute()
            return result
            
        except Exception as e:
            print(f"⚠️ Erro ao logar interação no Supabase: {e}")
            # Não queremos que falhas de log paralisem o fluxo principal
            return None
            
    def update_campaign(self, contact_id, update_data):
        """
        Atualiza ou cria registro de campanha para um contato
        """
        if not self.client:
            return None

        try:
            # Primeiro verifica se já existe
            existing = self.client.table("nps_campaigns").select("*").eq("contact_id", str(contact_id)).execute()
            
            if existing.data:
                # Update
                result = self.client.table("nps_campaigns").update(update_data).eq("contact_id", str(contact_id)).execute()
            else:
                # Insert
                update_data["contact_id"] = str(contact_id)
                result = self.client.table("nps_campaigns").insert(update_data).execute()
                
            return result
        except Exception as e:
            print(f"⚠️ Erro ao atualizar campanha no Supabase: {e}")
            return None

# Instância global para facilitar importação
supabase_client = SupabaseClient()
