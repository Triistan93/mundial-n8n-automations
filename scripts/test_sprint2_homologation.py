# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"

instance_name = f"homolog_s2_{int(time.time())}"

print("=================================================================")
print("  DISPARANDO TESTE E2E DA SPRINT 2 (NOTIFICAÇÃO INSTANTÂNEA IM)   ")
print("=================================================================\n")

# Turno 1: Abertura do Lead com Alta Intenção (Lead Quente)
p1 = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": instance_name,
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_S2_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Olá, sou o Eduardo Alaminos de Americana. Quero comprar uma Honda CB 300F Twister Zero KM à vista no Pix hoje mesmo! Tenho R$ 10.000 de entrada e quero fechar o negócio agora."
        },
        "messageTimestamp": int(time.time())
    }
}

print("--- [TURNO 1] ENVIANDO MENSAGEM DO CLIENTE ---")
r1 = requests.post(WEBHOOK_URL, json=p1, timeout=30)
print(f"Turno 1 disparado: HTTP {r1.status_code}")
print("Aguardando 20 segundos para a IA processar e responder...")
time.sleep(20)

# Turno 2: Confirmação e Encerramento para Transferência
p2 = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": instance_name,
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_S2_T2_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Unidade de Americana sim! Meu WhatsApp é 19991859143. Pode transferir para o consultor fechar o pedido comigo por favor!"
        },
        "messageTimestamp": int(time.time())
    }
}

print("\n--- [TURNO 2] ENVIANDO CONFIRMAÇÃO DO CLIENTE ---")
r2 = requests.post(WEBHOOK_URL, json=p2, timeout=30)
print(f"Turno 2 disparado: HTTP {r2.status_code}")
print("Aguardando 25 segundos para o n8n processar a qualificação, criar o Deal no CRM e disparar a notificação IM...")
time.sleep(25)

# 1. Consultar Deal na Categoria 18
print("\n--- 1. CONSULTANDO BITRIX24: BUSCANDO O CARD GERADO NA CATEGORIA 18 ---")
b24_search = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json?filter[CATEGORY_ID]=18&order[ID]=DESC&limit=2&select[0]=ID&select[1]=TITLE&select[2]=STAGE_ID&select[3]=CATEGORY_ID&select[4]=ASSIGNED_BY_ID&select[5]=DATE_CREATE"
r_b24 = requests.get(b24_search)

deal_id = None
if r_b24.status_code == 200:
    deals = r_b24.json().get('result', [])
    if deals:
        latest = deals[0]
        deal_id = latest.get('ID')
        print(f"• Deal ID: #{deal_id}")
        print(f"  Título: {latest.get('TITLE')}")
        print(f"  Categoria: {latest.get('CATEGORY_ID')} (Vendas Outras Mídias)")
        print(f"  Etapa: {latest.get('STAGE_ID')}")
        print(f"  Responsável: {latest.get('ASSIGNED_BY_ID')} (Eduardo Alaminos)")
        print(f"  Link: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{deal_id}/")

# 2. Consultar as últimas mensagens no Chat do Eduardo Alaminos (DIALOG_ID: 32598)
print("\n--- 2. CONSULTANDO BITRIX24: BUSCANDO A NOTIFICAÇÃO NO CHAT PRIVADO ---")
im_search = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/im.dialog.messages.get.json?DIALOG_ID=32598&LIMIT=3"
r_im = requests.get(im_search)

if r_im.status_code == 200:
    messages = r_im.json().get('result', {}).get('messages', [])
    print(f"Mensagens recentes encontradas no chat: {len(messages)}")
    for m in messages[:2]:
        msg_id = m.get('id')
        author_id = m.get('author_id')
        text = m.get('text', '')
        date = m.get('date')
        print(f"\n• Mensagem ID #{msg_id} (Autor #{author_id} - Sophia):")
        print(f"  Data: {date}")
        print(f"  Conteúdo:\n{text[:400]}")
else:
    print("Erro ao consultar mensagens IM:", r_im.text)
