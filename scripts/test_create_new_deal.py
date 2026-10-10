# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"

# Turno 1: Cliente inicia
p1 = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": "homolog_c18",
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_C18_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Olá, sou o Eduardo Alaminos de Franca e quero comprar uma Honda Sahara 300 Zero KM à vista no Pix! Pode me passar os valores?"
        },
        "messageTimestamp": int(time.time())
    }
}

print("--- DISPARANDO TURNO 1 (Abertura do Lead) ---")
r1 = requests.post(WEBHOOK_URL, json=p1, timeout=30)
print(f"Turno 1 disparado: HTTP {r1.status_code}")
print("Aguardando 20 segundos para a IA responder no WhatsApp...")
time.sleep(20)

# Turno 2: Cliente confirma telefone e pede transferência
p2 = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": "homolog_c18",
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_C18_T2_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Sim, à vista no Pix! Meu WhatsApp é 19991859143, pode transferir para o especialista fechar o pedido comigo agora!"
        },
        "messageTimestamp": int(time.time())
    }
}

print("\n--- DISPARANDO TURNO 2 (Confirmação e Qualificação Final) ---")
r2 = requests.post(WEBHOOK_URL, json=p2, timeout=30)
print(f"Turno 2 disparado: HTTP {r2.status_code}")
print("Aguardando 25 segundos para o n8n processar o buffer, a LLM e criar o NOVO CARD no Bitrix24 (Categoria 18)...")
time.sleep(25)

# Buscar o novo card criado na Categoria 18
print("\n--- CONSULTANDO BITRIX24: BUSCANDO NOVO CARD NA CATEGORIA 18 (Vendas Outras Mídias) ---")
b24_search = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.deal.list.json?filter[CATEGORY_ID]=18&order[ID]=DESC&limit=5&select[0]=ID&select[1]=TITLE&select[2]=STAGE_ID&select[3]=CATEGORY_ID&select[4]=ASSIGNED_BY_ID&select[5]=DATE_CREATE"
r_b24 = requests.get(b24_search)

if r_b24.status_code == 200:
    deals = r_b24.json().get('result', [])
    print(f"Deals retornados na Categoria 18: {len(deals)}")
    for d in deals:
        print(f"\n• Deal ID: #{d.get('ID')}")
        print(f"  Título: {d.get('TITLE')}")
        print(f"  Categoria: {d.get('CATEGORY_ID')} (Vendas Outras Mídias)")
        print(f"  Etapa: {d.get('STAGE_ID')}")
        print(f"  Criado em: {d.get('DATE_CREATE')}")
        print(f"  Responsável: {d.get('ASSIGNED_BY_ID')} {'(✅ MATCH COM EDUARDO ALAMINOS #32598!)' if str(d.get('ASSIGNED_BY_ID')) == '32598' else ''}")
        print(f"  Link: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{d.get('ID')}/")
else:
    print("Erro ao consultar Bitrix:", r_b24.text)
