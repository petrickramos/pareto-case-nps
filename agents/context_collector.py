"""
Agente Coletor de Contexto
Responsável por buscar e consolidar todos os dados do cliente no HubSpot Mock
"""

from hubspot_client import HubSpotClient
from typing import Dict, Any


class ContextCollectorAgent:
    def __init__(self):
        self.hubspot = HubSpotClient()
    
    def collect(self, contact_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Coleta contexto completo de um contato do HubSpot
        
        Args:
            contact_id: ID do contato no HubSpot
            days_back: Quantos dias de histórico buscar (default: 30)
            
        Returns:
            Dict com contexto estruturado do cliente
        """
        print(f"🔍 Coletando contexto do cliente {contact_id}...")
        
        # Buscar todos os dados do contato
        context = self.hubspot.get_contact_context(contact_id, days_back)
        
        # Formatar resumo estruturado
        formatted_context = self._format_context(context)
        
        print(f"✅ Contexto coletado: {len(context['deals'])} deals, "
              f"{len(context['tickets'])} tickets, "
              f"{len(context['emails'])} emails")
        
        return formatted_context
    
    def _format_context(self, context: Dict) -> Dict[str, Any]:
        """Formata o contexto em estrutura legível para outros agentes"""
        
        # Tratamento seguro para contato (pode ser dict ou list)
        contact = context.get("contact", {})
        if isinstance(contact, list):
            # Se for lista, pega o primeiro item ou usa dict vazio
            contact = contact[0] if contact else {}
        elif not isinstance(contact, dict):
            # Se não for dict nem list, usa dict vazio
            contact = {}
        
        # Tratamento seguro para propriedades (pode ser dict ou list)
        props = contact.get("properties", {}) if isinstance(contact, dict) else {}
        if isinstance(props, list):
            props = props[0] if props else {}
        
        formatted = {
            "cliente": {
                "id": context["contact_id"],
                "nome": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                "email": props.get("email", "N/A"),
                "telefone": props.get("phone", "N/A"),
                "tempo_como_cliente": self._calculate_tenure(str(props.get("createdate", ""))),
                "tag_csat": props.get("mock_csat_survey", "false")
            },
            "negocios": [],
            "tickets": [],
            "emails": [],
            "anotacoes": [],
            "metricas": {
                "valor_total": context.get("consolidated_value", 0),
                "quantidade_deals": len(context.get("deals", [])),
                "quantidade_tickets": len(context.get("tickets", [])),
                "quantidade_emails": len(context.get("emails", [])),
                "quantidade_anotacoes": len(context.get("notes", [])),
                "riscos_identificados": len(context.get("risks", []))
            },
            "riscos": context.get("risks", [])
        }
        
        # Formatar deals
        for deal in context.get("deals", []):
            # Tratamento seguro para deal
            if isinstance(deal, list):
                deal = deal[0] if deal else {}
            if not isinstance(deal, dict):
                continue
            deal_props = deal.get("properties", {}) if isinstance(deal.get("properties"), dict) else {}
            formatted["negocios"].append({
                "id": deal.get("id") if isinstance(deal, dict) else None,
                "nome": deal_props.get("dealname", "Sem nome") if isinstance(deal_props, dict) else "Sem nome",
                "valor": float(deal_props.get("amount", 0) or 0) if isinstance(deal_props, dict) else 0,
                "fase": deal_props.get("dealstage", "N/A") if isinstance(deal_props, dict) else "N/A",
                "data_criacao": deal_props.get("createdate", "N/A") if isinstance(deal_props, dict) else "N/A"
            })
        
        # Formatar tickets
        for ticket in context.get("tickets", []):
            # Tratamento seguro para ticket
            if isinstance(ticket, list):
                ticket = ticket[0] if ticket else {}
            if not isinstance(ticket, dict):
                continue
            ticket_props = ticket.get("properties", {}) if isinstance(ticket.get("properties"), dict) else {}
            formatted["tickets"].append({
                "id": ticket.get("id") if isinstance(ticket, dict) else None,
                "assunto": ticket_props.get("subject", "Sem assunto") if isinstance(ticket_props, dict) else "Sem assunto",
                "categoria": ticket_props.get("hs_ticket_category", "N/A") if isinstance(ticket_props, dict) else "N/A",
                "prioridade": ticket_props.get("hs_ticket_priority", "N/A") if isinstance(ticket_props, dict) else "N/A",
                "data_criacao": ticket_props.get("createdate", "N/A") if isinstance(ticket_props, dict) else "N/A"
            })
        
        # Formatar emails
        for email in context.get("emails", []):
            # Tratamento seguro para email
            if isinstance(email, list):
                email = email[0] if email else {}
            if not isinstance(email, dict):
                continue
            email_props = email.get("properties", {}) if isinstance(email.get("properties"), dict) else {}
            email_text = email_props.get("hs_email_text", "N/A") if isinstance(email_props, dict) else "N/A"
            formatted["emails"].append({
                "id": email.get("id") if isinstance(email, dict) else None,
                "assunto": email_props.get("hs_email_subject", "Sem assunto") if isinstance(email_props, dict) else "Sem assunto",
                "texto": (email_text[:200] + "..." if len(email_text) > 200 else email_text) if isinstance(email_text, str) else "N/A",
                "data": email_props.get("hs_timestamp", "N/A") if isinstance(email_props, dict) else "N/A",
                "direcao": email_props.get("hs_email_direction", "N/A") if isinstance(email_props, dict) else "N/A"
            })
        
        # Formatar notes
        for note in context.get("notes", []):
            # Tratamento seguro para note
            if isinstance(note, list):
                note = note[0] if note else {}
            if not isinstance(note, dict):
                continue
            note_props = note.get("properties", {}) if isinstance(note.get("properties"), dict) else {}
            note_body = note_props.get("hs_note_body", "N/A") if isinstance(note_props, dict) else "N/A"
            formatted["anotacoes"].append({
                "id": note.get("id") if isinstance(note, dict) else None,
                "conteudo": (note_body[:200] + "..." if len(note_body) > 200 else note_body) if isinstance(note_body, str) else "N/A",
                "data": note_props.get("hs_timestamp", "N/A") if isinstance(note_props, dict) else "N/A"
            })
        
        return formatted
    
    def _calculate_tenure(self, createdate: str) -> str:
        """Calcula tempo como cliente em dias/meses"""
        if not createdate:
            return "N/A"
        
        try:
            from datetime import datetime
            # Converter timestamp do HubSpot (ms) para datetime
            timestamp_ms = int(createdate)
            created = datetime.fromtimestamp(timestamp_ms / 1000)
            now = datetime.now()
            
            delta = now - created
            days = delta.days
            
            if days < 30:
                return f"{days} dias"
            elif days < 365:
                months = days // 30
                return f"{months} meses"
            else:
                years = days // 365
                months = (days % 365) // 30
                return f"{years} anos e {months} meses"
        except:
            return "N/A"


if __name__ == "__main__":
    print("🧪 Testando Agente Coletor de Contexto")
    print("=" * 60)
    
    agent = ContextCollectorAgent()
    
    # Testar com contact_id 101
    contact_id = "101"
    context = agent.collect(contact_id)
    
    print("\n📊 Resumo do Contexto:")
    print(f"Cliente: {context['cliente']['nome']}")
    print(f"Email: {context['cliente']['email']}")
    print(f"Tempo como cliente: {context['cliente']['tempo_como_cliente']}")
    print(f"Valor total: R$ {context['metricas']['valor_total']:,.2f}")
    print(f"Riscos: {context['metricas']['riscos_identificados']}")
    
    if context['riscos']:
        print("\n⚠️ Riscos Identificados:")
        for risco in context['riscos']:
            print(f"  - {risco['description']}")
