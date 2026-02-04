"""
Script para criar tabela conversation_messages no Supabase via API
Executa o SQL automaticamente usando as credenciais do .env
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

def setup_conversation_table():
    """Cria tabela conversation_messages no Supabase"""
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Erro: Credenciais Supabase não encontradas no .env")
        return False
    
    print("🔧 Conectando ao Supabase...")
    print(f"URL: {url}")
    
    try:
        client = create_client(url, key)
        
        # SQL para criar tabela
        sql = """
        CREATE TABLE IF NOT EXISTS conversation_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chat_id TEXT NOT NULL,
            message_text TEXT NOT NULL,
            sender TEXT NOT NULL CHECK (sender IN ('user', 'bot', 'manager', 'system')),
            conversation_state TEXT,
            nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),
            sentiment TEXT,
            manual_mode BOOLEAN DEFAULT false,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_conversation_chat_id ON conversation_messages(chat_id);
        CREATE INDEX IF NOT EXISTS idx_conversation_created_at ON conversation_messages(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_conversation_sender ON conversation_messages(sender);
        CREATE INDEX IF NOT EXISTS idx_conversation_state ON conversation_messages(conversation_state);
        """
        
        print("📝 Executando SQL...")
        
        # Nota: Supabase Python client não tem método direto para executar SQL DDL
        # Precisamos usar a REST API ou fazer via dashboard
        
        print("\n⚠️ ATENÇÃO:")
        print("O Supabase Python client não suporta execução direta de SQL DDL.")
        print("\nVocê precisa executar o SQL manualmente:")
        print("1. Acesse: https://supabase.com/dashboard")
        print("2. Selecione seu projeto")
        print("3. Vá em 'SQL Editor'")
        print("4. Cole e execute o SQL abaixo:")
        print("\n" + "="*60)
        print(sql)
        print("="*60)
        
        # Verificar se tabela já existe tentando fazer uma query
        try:
            result = client.table("conversation_messages").select("*").limit(1).execute()
            print("\n✅ Tabela 'conversation_messages' já existe!")
            print(f"Registros encontrados: {len(result.data)}")
            return True
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("\n❌ Tabela 'conversation_messages' NÃO existe ainda.")
                print("Execute o SQL acima no dashboard do Supabase.")
                return False
            else:
                print(f"\n⚠️ Erro ao verificar tabela: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🚀 Setup Supabase - Tabela conversation_messages")
    print("="*60)
    
    success = setup_conversation_table()
    
    if success:
        print("\n✅ Setup concluído com sucesso!")
    else:
        print("\n⚠️ Ação manual necessária - veja instruções acima")
