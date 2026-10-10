# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"

p3 = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": "homolog_c18",
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_C18_T3_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Pode ser a unidade de Campinas então! Meu WhatsApp é 19991859143, pode transferir para o vendedor de Campinas agora por favor!"
        },
        "messageTimestamp": int(time.time())
    }
}

print("--- DISPARANDO TURNO 3 (Confirmando Campinas e Encerrando Triagem) ---")
r = requests.post(WEBHOOK_URL, json=p3, timeout=30)
print(f"HTTP Response: {r.status_code}")
print("Aguardando 25s para processamento do n8n...")
time.sleep(25)

b24_search = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json?filter[CATEGORY_ID]=18&order[ID]=DESC&limit=3&select[0]=ID&select[1]=TITLE&select[2]=STAGE_ID&select[3]=CATEGORY_ID&select[4]=ASSIGNED_BY_ID&select[5]=DATE_CREATE"
r_b24 = requests.get(b24_search)
deals = r_b24.json().get('result', [])
print(f"\nDeals encontrados na Categoria 18: {len(deals)}")
for d in deals:
    deal_id = d.get('ID')
    title = d.get('TITLE')
    cat = d.get('CATEGORY_ID')
    resp = d.get('ASSIGNED_BY_ID')
    created = d.get('DATE_CREATE')
    print(f"• Deal ID: #{deal_id} | Título: {title} | Cat: {cat} | Resp: {resp} | Criado: {created}")
    print(f"  Link: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{deal_id}/")
