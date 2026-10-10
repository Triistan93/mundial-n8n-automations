# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"

payload = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": "homolog",
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_SPRINT1_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Sim, exatamente, financiamento da diferença com a moto e o dinheiro de entrada! Meu WhatsApp com DDD é 19991859143. Pode transferir para o especialista agora por favor!"
        },
        "messageTimestamp": int(time.time())
    }
}

print("=================================================================")
print("  DISPARANDO TESTE E2E NO CLONE DE HOMOLOGAÇÃO (SPRINT 1)       ")
print("=================================================================\n")
print(f"URL: {WEBHOOK_URL}")
print(f"Lead: {payload['data']['pushName']} ({payload['data']['key']['remoteJid']})")
print(f"Mensagem: \"{payload['data']['message']['conversation']}\"\n")

t0 = time.time()
try:
    r = requests.post(WEBHOOK_URL, json=payload, timeout=45)
    print(f"Resposta do Webhook: HTTP {r.status_code}")
    print(f"Conteúdo retornado: {r.text[:300]}")
except Exception as e:
    print(f"Exceção no disparo: {e}")

print(f"\nTempo decorrido no envio: {time.time() - t0:.1f} segundos")
print("Aguardando 30 segundos para o n8n processar o buffer (15s), a LLM e a criação no CRM...")
time.sleep(30)

# Consultar na API do Bitrix se o Deal foi criado/atualizado com o Eduardo Alaminos (#32598)
print("\n--- CONSULTANDO BITRIX24: BUSCANDO O CARD DE TESTE ---")
b24_search_eduardo = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json?filter[CATEGORY_ID]=18&filter[ASSIGNED_BY_ID]=32598&order[ID]=DESC&limit=3&select[0]=ID&select[1]=TITLE&select[2]=STAGE_ID&select[3]=ASSIGNED_BY_ID&select[4]=MODIFY_BY_ID&select[5]=DATE_MODIFY&select[6]=DATE_CREATE"
r_b24 = requests.get(b24_search_eduardo)

if r_b24.status_code == 200:
    deals = r_b24.json().get('result', [])
    print(f"Cards encontrados para Eduardo Alaminos (#32598): {len(deals)}")
    for d in deals:
        deal_id = d.get('ID')
        title = d.get('TITLE')
        assigned = d.get('ASSIGNED_BY_ID')
        stage = d.get('STAGE_ID')
        created = d.get('DATE_CREATE')
        print(f"\n• Deal ID: #{deal_id}")
        print(f"  Título: {title}")
        print(f"  Criado em: {created}")
        print(f"  Responsável (ASSIGNED_BY_ID): {assigned} (✅ EDUARDO ALAMINOS)")
        print(f"  Etapa: {stage}")
        print(f"  Link: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{deal_id}/")
        
        # Buscar comentário na timeline
        r_comm = requests.get(f"https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.timeline.comment.list.json?filter[ENTITY_ID]={deal_id}&filter[ENTITY_TYPE]=deal")
        if r_comm.status_code == 200:
            comms = r_comm.json().get('result', [])
            if comms:
                print("  Comentário na Timeline:")
                print("  " + comms[0].get('COMMENT', ''))
else:
    print("Erro ao consultar Bitrix:", r_b24.text)
