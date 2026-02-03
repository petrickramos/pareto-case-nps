import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class HubSpotClient:
    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY", "pat-na1-123")
        self.base_url = os.getenv("HUBSPOT_API_URL", "http://localhost:4010")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search_contacts(self, filters=None, properties=None, limit=10):
        """Busca contatos no HubSpot com filtros opcionais"""
        url = f"{self.base_url}/crm/v3/objects/contacts/search"
        
        payload = {
            "filterGroups": filters or [],
            "limit": limit
        }
        
        if properties:
            payload["properties"] = properties
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contatos: {e}")
            return None
    
    def search_deals(self, contact_id: str, created_after: int = 0) -> Optional[Dict]:
        """Busca deals associados a um contato"""
        url = f"{self.base_url}/crm/v3/objects/deals/search"
        
        filters = [{
            "filters": [
                {"propertyName": "associations.contact", "operator": "EQ", "value": contact_id},
                {"propertyName": "createdate", "operator": "GTE", "value": str(created_after)}
            ]
        }]
        
        payload = {
            "filterGroups": filters,
            "limit": 100
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar deals: {e}")
            return None
    
    def search_tickets(self, contact_id: str, created_after: int = 0) -> Optional[Dict]:
        """Busca tickets (churn/downgrade) associados a um contato"""
        url = f"{self.base_url}/crm/v3/objects/tickets/search"
        
        filters = [{
            "filters": [
                {"propertyName": "associations.contact", "operator": "EQ", "value": contact_id},
                {"propertyName": "createdate", "operator": "GTE", "value": str(created_after)}
            ]
        }]
        
        payload = {
            "filterGroups": filters,
            "limit": 100
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar tickets: {e}")
            return None
    
    def search_emails(self, contact_id: str, created_after: int = 0) -> Optional[Dict]:
        """Busca emails associados a um contato"""
        url = f"{self.base_url}/crm/v3/objects/emails/search"
        
        filters = [{
            "filters": [
                {"propertyName": "associations.contact", "operator": "EQ", "value": contact_id},
                {"propertyName": "createdate", "operator": "GTE", "value": str(created_after)}
            ]
        }]
        
        payload = {
            "filterGroups": filters,
            "limit": 100
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar emails: {e}")
            return None
    
    def search_notes(self, contact_id: str, created_after: int = 0) -> Optional[Dict]:
        """Busca anotações associadas a um contato"""
        url = f"{self.base_url}/crm/v3/objects/notes/search"
        
        filters = [{
            "filters": [
                {"propertyName": "associations.contact", "operator": "EQ", "value": contact_id},
                {"propertyName": "createdate", "operator": "GTE", "value": str(created_after)}
            ]
        }]
        
        payload = {
            "filterGroups": filters,
            "limit": 100
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar notes: {e}")
            return None
    
    def get_deal_line_items(self, deal_id: str) -> Optional[List[Dict]]:
        """Busca line items (produtos) de um deal específico"""
        url = f"{self.base_url}/crm/v4/objects/deals/{deal_id}/associations/line_items"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar line items do deal {deal_id}: {e}")
            return None
    
    def get_contact_context(self, contact_id: str, days_back: int = 30) -> Dict:
        """
        Coleta contexto completo de um contato
        Retorna dict consolidado com: contato, deals, tickets, emails, notes
        """
        # Calcular timestamp de corte (dias atrás em ms)
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)
        created_after = int(cutoff_date.timestamp() * 1000)
        
        context = {
            "contact_id": contact_id,
            "contact": None,
            "deals": [],
            "tickets": [],
            "emails": [],
            "notes": [],
            "line_items": [],
            "consolidated_value": 0.0,
            "risks": []
        }
        
        # Buscar dados do contato
        contact_filters = [{
            "filters": [{"propertyName": "hs_object_id", "operator": "EQ", "value": contact_id}]
        }]
        contact_data = self.search_contacts(filters=contact_filters)
        if contact_data:
            if isinstance(contact_data, dict):
                results = contact_data.get("results", [])
                if results:
                    context["contact"] = results[0]
            elif isinstance(contact_data, list) and contact_data:
                context["contact"] = contact_data[0]
        
        # Buscar deals
        deals_data = self.search_deals(contact_id, created_after)
        if deals_data:
            if isinstance(deals_data, dict):
                context["deals"] = deals_data.get("results", [])
            elif isinstance(deals_data, list):
                context["deals"] = deals_data
            else:
                context["deals"] = []
            
            # Para cada deal, buscar line items
            for deal in context["deals"]:
                # Proteção: deal pode ser lista ou dict
                if isinstance(deal, list):
                    deal = deal[0] if deal else {}
                if not isinstance(deal, dict):
                    continue
                deal_id = deal.get("id") if isinstance(deal, dict) else None
                if not deal_id:
                    continue
                line_items = self.get_deal_line_items(deal_id)
                if line_items and isinstance(line_items, dict):
                    results = line_items.get("results", [])
                    if isinstance(results, list):
                        context["line_items"].extend(results)
                
                # Somar valor do deal - proteção para properties
                deal_props = deal.get("properties", {}) if isinstance(deal.get("properties"), dict) else {}
                if isinstance(deal_props, list):
                    deal_props = deal_props[0] if deal_props else {}
                amount = deal_props.get("amount", "0") if isinstance(deal_props, dict) else "0"
                try:
                    context["consolidated_value"] += float(amount)
                except:
                    pass
        
        # Buscar tickets (indicadores de churn/risco)
        tickets_data = self.search_tickets(contact_id, created_after)
        if tickets_data:
            if isinstance(tickets_data, dict):
                context["tickets"] = tickets_data.get("results", [])
            elif isinstance(tickets_data, list):
                context["tickets"] = tickets_data
            else:
                context["tickets"] = []
            
            # Identificar riscos
            for ticket in context["tickets"]:
                # Proteção: ticket pode ser lista ou dict
                if isinstance(ticket, list):
                    ticket = ticket[0] if ticket else {}
                if not isinstance(ticket, dict):
                    continue
                
                # Proteção: properties pode ser lista ou dict
                ticket_props = ticket.get("properties", {}) if isinstance(ticket, dict) else {}
                if isinstance(ticket_props, list):
                    ticket_props = ticket_props[0] if ticket_props else {}
                
                subject = ticket_props.get("subject", "") if isinstance(ticket_props, dict) else ""
                subject = subject.lower() if isinstance(subject, str) else ""
                
                if any(word in subject for word in ["cancel", "churn", "downgrade", "problema", "reclama"]):
                    context["risks"].append({
                        "type": "ticket",
                        "id": ticket.get("id") if isinstance(ticket, dict) else None,
                        "description": subject
                    })
        
        # Buscar emails
        emails_data = self.search_emails(contact_id, created_after)
        if emails_data:
            if isinstance(emails_data, dict):
                context["emails"] = emails_data.get("results", [])
            elif isinstance(emails_data, list):
                context["emails"] = emails_data
            else:
                context["emails"] = []
        
        # Buscar notes
        notes_data = self.search_notes(contact_id, created_after)
        if notes_data:
            if isinstance(notes_data, dict):
                context["notes"] = notes_data.get("results", [])
            elif isinstance(notes_data, list):
                context["notes"] = notes_data
            else:
                context["notes"] = []
        
        return context


if __name__ == "__main__":
    print("🔗 Testando conexão com Mock HubSpot...")
    print("=" * 50)
    
    client = HubSpotClient()
    
    # Testar busca de contatos
    print("\n📋 Buscando contatos elegíveis:")
    filters = [{
        "filters": [{"propertyName": "mock_csat_survey", "operator": "EQ", "value": "true"}]
    }]
    
    contacts = client.search_contacts(filters=filters, limit=5)
    
    if contacts:
        print(f"✅ Encontrados {contacts.get('total', 0)} contatos\n")
        
        for contact in contacts.get("results", [])[:2]:
            contact_id = contact.get("id")
            props = contact.get("properties", {})
            print(f"ID: {contact_id}")
            print(f"Nome: {props.get('firstname', '')} {props.get('lastname', '')}")
            print(f"Email: {props.get('email', 'N/A')}")
            print(f"Tag CSAT: {props.get('mock_csat_survey', 'N/A')}")
            
            # Testar contexto completo
            print("\n📊 Buscando contexto completo...")
            context = client.get_contact_context(contact_id, days_back=30)
            print(f"   Deals: {len(context['deals'])}")
            print(f"   Tickets: {len(context['tickets'])}")
            print(f"   Emails: {len(context['emails'])}")
            print(f"   Notes: {len(context['notes'])}")
            print(f"   Valor Total: R$ {context['consolidated_value']:,.2f}")
            if context['risks']:
                print(f"   ⚠️ Riscos: {len(context['risks'])}")
            print("-" * 40)
    else:
        print("❌ Falha ao conectar com Mock HubSpot")
