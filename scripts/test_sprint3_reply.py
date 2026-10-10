# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"

# Buscar a instância usada no teste 567609
headers = {"X-N8N-API-KEY": N8N_API_KEY}
r = requests.get("https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/567609?includeData=true", headers=headers)
prep = r.json().get('data', {}).get('resultData', {}).get('runData', {}).get('Preparar Contexto de Follow-Up (Sprint 3)', [{}])[0].get('data', {}).get('main', [[{}]])[0][0].get('json', {})
instance_name = prep.get('instance')
print(f"Instância do teste anterior: {instance_name}")

# Cliente responde após receber a mensagem de resgate no WhatsApp
payload = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": instance_name,
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_S3_REPLY_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Opa, desculpa a correria! A compra da Titan 160 seria à vista no Pix sim, e sou de Americana. Meu WhatsApp é 19991859143, pode me transferir para o consultor de Americana por favor!"
        },
        "messageTimestamp": int(time.time())
    }
}

print("Enviando resposta do cliente após o resgate...")
r_post = requests.post(WEBHOOK_URL, json=payload, timeout=30)
print(f"Webhook HTTP: {r_post.status_code}")
print("Aguardando 25s para o n8n qualificar, gerar o deal no Bitrix e disparar a notificação...")
time.sleep(25)

# Verificar se criou o deal no Bitrix
b24 = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json?filter[CATEGORY_ID]=18&order[ID]=DESC&limit=1"
r_b24 = requests.get(b24)
deals = r_b24.json().get('result', [])
if deals:
    d = deals[0]
    deal_id = d.get('ID')
    title = d.get('TITLE')
    resp = d.get('ASSIGNED_BY_ID')
    print(f"\n🎉 NOVO DEAL CRIADO APÓS O RESGATE: #{deal_id} - {title} (Responsável #{resp})")
    print(f"Link: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{deal_id}/")

# Verificar notificação instantânea IM
r_im = requests.get("https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/im.dialog.messages.get.json?DIALOG_ID=32598&LIMIT=1")
if r_im.status_code == 200:
    msg = r_im.json().get('result', {}).get('messages', [])[0]
    print(f"\n📲 Notificação IM (ID #{msg.get('id')}):")
    print(msg.get('text')[:350])
