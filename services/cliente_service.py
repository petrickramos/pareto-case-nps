"""
Cliente Service - Integração com HubSpot Mock API
Responsável por buscar dados de clientes e coletar contexto
"""

import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class ClienteService:
    """Serviço para buscar e gerenciar dados de clientes do HubSpot Mock"""
    
    def __init__(self):
        self.hubspot_base = os.getenv("HUBSPOT_MOCK_URL", "http://localhost:8080")
        self.hubspot_token = os.getenv("HUBSPOT_TOKEN", "pat-na1-123")
        self.headers = {
            "Authorization": f"Bearer {self.hubspot_token}",
            "Content-Type": "application/json"
        }
        self.cache: Dict[str, Dict] = {}  # Cache em memória
    
    def buscar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca cliente no HubSpot Mock por email
        
        Args:
            email: Email do cliente
            
        Returns:
            Dados do cliente ou None se não encontrado
        """
        # Verificar cache
        if email in self.cache:
            print(f"✅ Cliente {email} encontrado no cache")
            return self.cache[email]
        
        url = f"{self.hubspot_base}/crm/v3/objects/contacts/search"
        
        payload = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email
                }]
            }],
            "properties": ["email", "firstname", "lastname", "phone", "mobilephone"],
            "limit": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if results:
                cliente = results[0]
                # Armazenar em cache
                self.cache[email] = cliente
                print(f"✅ Cliente {email} encontrado no HubSpot Mock")
                return cliente
            
            print(f"⚠️ Cliente {email} não encontrado no HubSpot Mock")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar cliente {email}: {e}")
            return None
    
    def buscar_por_chat_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca cliente no cache por chat_id do Telegram
        
        Args:
            chat_id: ID do chat do Telegram
            
        Returns:
            Dados do cliente ou None
        """
        # TODO: Implementar busca no Supabase por chat_id
        # Por enquanto, retorna None (fallback para busca por email)
        return None
    
    def coletar_contexto(self, contact_id: str) -> Dict[str, Any]:
        """
        Coleta contexto completo do cliente (deals, tickets, notes, emails)
        
        Args:
            contact_id: ID do contato no HubSpot
            
        Returns:
            Dict com contexto completo
        """
        # Timestamp de 30 dias atrás (em milissegundos)
        cutoff = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        contexto = {
            "deals": self._buscar_deals(contact_id, cutoff),
            "tickets": self._buscar_tickets(contact_id, cutoff),
            "notes": self._buscar_notes(contact_id, cutoff),
            "emails": self._buscar_emails(contact_id, cutoff)
        }
        
        # Calcular métricas
        contexto["metricas"] = {
            "num_deals": len(contexto["deals"]),
            "num_tickets": len(contexto["tickets"]),
            "num_notes": len(contexto["notes"]),
            "num_emails": len(contexto["emails"]),
            "valor_total": sum(
                float(d.get("properties", {}).get("amount", 0) or 0) 
                for d in contexto["deals"]
            )
        }
        
        print(f"✅ Contexto coletado: {contexto['metricas']}")
        return contexto
    
    def _buscar_deals(self, contact_id: str, cutoff: int) -> List[Dict]:
        """Busca negócios do cliente"""
        url = f"{self.hubspot_base}/crm/v3/objects/deals/search"
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "associations.contact",
                        "operator": "EQ",
                        "value": contact_id
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": str(cutoff)
                    }
                ]
            }],
            "limit": 100
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"⚠️ Erro ao buscar deals: {e}")
            return []
    
    def _buscar_tickets(self, contact_id: str, cutoff: int) -> List[Dict]:
        """Busca tickets do cliente"""
        url = f"{self.hubspot_base}/crm/v3/objects/tickets/search"
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "associations.contact",
                        "operator": "EQ",
                        "value": contact_id
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": str(cutoff)
                    }
                ]
            }],
            "limit": 100
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"⚠️ Erro ao buscar tickets: {e}")
            return []
    
    def _buscar_notes(self, contact_id: str, cutoff: int) -> List[Dict]:
        """Busca anotações do cliente"""
        url = f"{self.hubspot_base}/crm/v3/objects/notes/search"
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "associations.contact",
                        "operator": "EQ",
                        "value": contact_id
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": str(cutoff)
                    }
                ]
            }],
            "limit": 100
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"⚠️ Erro ao buscar notes: {e}")
            return []
    
    def _buscar_emails(self, contact_id: str, cutoff: int) -> List[Dict]:
        """Busca emails do cliente"""
        url = f"{self.hubspot_base}/crm/v3/objects/emails/search"
        
        payload = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "associations.contact",
                        "operator": "EQ",
                        "value": contact_id
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": str(cutoff)
                    }
                ]
            }],
            "limit": 100
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"⚠️ Erro ao buscar emails: {e}")
            return []


# Singleton instance
cliente_service = ClienteService()
