#!/usr/bin/env python3
"""
Gera 12 testes de NPS (4 por tipo) e grava no Supabase em conversation_messages.
Uso:
  python3 generate_bulk_nps_tests.py
  python3 generate_bulk_nps_tests.py --per-type 4 --prefix test_nps
"""

import argparse
import time
from datetime import datetime
from typing import Dict, List

from supabase_client import supabase_client

SCORES_BY_TYPE: Dict[str, List[int]] = {
    "PROMOTOR": [9, 10, 9, 10],
    "NEUTRO": [7, 8, 7, 8],
    "DETRATOR": [0, 3, 4, 6],
}

TEMPLATES = {
    "PROMOTOR": {
        "sentiment": "POSITIVO",
        "user": "Minha nota foi {score}, gostei bastante do atendimento.",
        "bot": "Que alegria receber sua nota {score}! Obrigado pelo feedback positivo."
    },
    "NEUTRO": {
        "sentiment": "NEUTRO",
        "user": "Dou nota {score}. Foi ok, mas pode melhorar.",
        "bot": "Obrigado pela nota {score}. Se puder, conte o que podemos melhorar."
    },
    "DETRATOR": {
        "sentiment": "NEGATIVO",
        "user": "Minha nota foi {score}. Tive problemas e fiquei insatisfeito.",
        "bot": "Sinto muito pela nota {score}. Vamos analisar e melhorar o atendimento."
    }
}


def log_message(chat_id: str, text: str, sender: str, state: str, score, sentiment, run_id: str, category: str):
    supabase_client.log_conversation_message(
        chat_id=chat_id,
        message_text=text,
        sender=sender,
        conversation_state=state,
        nps_score=score,
        sentiment=sentiment,
        metadata={
            "seed": True,
            "run_id": run_id,
            "categoria": category
        }
    )


def main():
    parser = argparse.ArgumentParser(description="Gerar testes NPS em massa.")
    parser.add_argument("--per-type", type=int, default=4, help="Quantidade por tipo (default: 4)")
    parser.add_argument("--prefix", type=str, default="bulk_nps", help="Prefixo do chat_id")
    parser.add_argument("--sleep", type=float, default=0.05, help="Pausa entre inserts (segundos)")
    args = parser.parse_args()

    if not supabase_client.client:
        print("❌ Supabase nao configurado. Defina SUPABASE_URL e SUPABASE_KEY/ANON no .env.")
        return

    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    total = 0

    for category, scores in SCORES_BY_TYPE.items():
        template = TEMPLATES[category]
        for i in range(min(args.per_type, len(scores))):
            score = scores[i]
            chat_id = f"{args.prefix}_{category.lower()}_{i + 1:02d}_{run_id}"

            user_text = template["user"].format(score=score)
            bot_text = template["bot"].format(score=score)

            log_message(
                chat_id=chat_id,
                text=user_text,
                sender="user",
                state="waiting_score",
                score=None,
                sentiment=None,
                run_id=run_id,
                category=category
            )
            log_message(
                chat_id=chat_id,
                text=bot_text,
                sender="bot",
                state="completed",
                score=score,
                sentiment=template["sentiment"],
                run_id=run_id,
                category=category
            )

            total += 1
            time.sleep(args.sleep)

    print(f"✅ Gerados {total} testes (run_id={run_id}).")


if __name__ == "__main__":
    main()
