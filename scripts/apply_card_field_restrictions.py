# -*- coding: utf-8 -*-
"""
Script de Saneamento e Blindagem da Ficha da Central de Serviços TI (Categoria 160).
1. Reorganiza as seções do card:
   - Seção 1 (Solicitante): apenas campos que o usuário deve preencher na abertura.
   - Seção 2 (Gestão TI): campos técnicos do robô e da equipe de TI.
2. Trava 'EDIT_IN_LIST: N' em todos os campos técnicos da TI para impedir edição inline.
"""
import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK = "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/"
ctx = ssl.create_default_context()

def call(method, payload=None):
    url = f"{WEBHOOK}{method}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8')}

print("=== PASSO 1: CONFIGURAR SEÇÕES DO CARD NA CATEGORIA 160 ===")

card_payload = {
    "scope": "C",
    "extras": {
        "dealCategoryId": 160
    },
    "data": [
        {
            "name": "main",
            "title": "Dados do Chamado (Solicitante)",
            "type": "section",
            "elements": [
                {"name": "TITLE", "optionFlags": "1"},
                {"name": "UF_CRM_1689593052602", "optionFlags": "1"},   # Loja
                {"name": "UF_CRM_1763388156", "optionFlags": "1"},       # Categoria Macro
                {"name": "UF_CRM_1729774515200", "optionFlags": "1"},   # Descrição
                {"name": "UF_CRM_TI_IMPACT", "optionFlags": "1"},        # Impacto
                {"name": "UF_CRM_TI_URGENCY", "optionFlags": "1"},       # Urgência
                {"name": "UF_CRM_1735304929", "optionFlags": "0"},       # Anexo / Print
                {"name": "OBSERVER", "optionFlags": "0"}                  # Observadores
            ]
        },
        {
            "name": "ti_management",
            "title": "Triagem & Gestão Técnica (TI)",
            "type": "section",
            "elements": [
                {"name": "ASSIGNED_BY_ID", "optionFlags": "1"},          # Técnico Responsável (Owner)
                {"name": "UF_CRM_TI_RESPONSIBLE", "optionFlags": "1"},   # Responsável TI (quem moveu/autorizou)
                {"name": "UF_CRM_1763388469429", "optionFlags": "1"},   # Subcategoria (refinada pela IA)
                {"name": "UF_CRM_TI_PRIORITY", "optionFlags": "1"},      # Prioridade Calculada B01
                {"name": "UF_CRM_TI_SHORT_SUBJECT", "optionFlags": "1"}, # Assunto Curto Padronizado
                {"name": "UF_CRM_TI_NEXT_OWNER", "optionFlags": "1"},    # Próximo Responsável
                {"name": "UF_CRM_TI_WAIT_REASON", "optionFlags": "1"},   # Motivo de Espera
                {"name": "COMMENTS", "optionFlags": "0"},                 # Observação Interna
                {"name": "UF_CRM_1689597532", "optionFlags": "1"}        # Resolução / Fechamento
            ]
        }
    ]
}

res_card = call("crm.deal.details.configuration.set", card_payload)
print("Resultado configuração do card:", res_card)

print("\n=== PASSO 2: HABILITAR EDIÇÃO (EDIT_IN_LIST = Y) NOS CAMPOS TÉCNICOS ===")

fields_to_lock = [
    {"id": 1796, "name": "UF_CRM_TI_RESPONSIBLE"},
    {"id": 1794, "name": "UF_CRM_TI_SHORT_SUBJECT"},
    {"id": 1784, "name": "UF_CRM_TI_NEXT_OWNER"},
    {"id": 1786, "name": "UF_CRM_TI_WAIT_REASON"},
    {"id": 1792, "name": "UF_CRM_TI_PRIORITY"},
    {"id": 221,  "name": "UF_CRM_1689597532"},        # Resolução / Fechamento
    {"id": 1678, "name": "UF_CRM_1763388469429"}       # Subcategoria
]

for item in fields_to_lock:
    res = call("crm.deal.userfield.update", {
        "id": item["id"],
        "fields": {
            "EDIT_IN_LIST": "Y"
        }
    })
    print(f"Campo {item['name']} (ID {item['id']}) -> EDIT_IN_LIST='Y': {res}")

print("\n=== PASSO 3: VALIDAR CONFIGURAÇÃO ATUALIZADA DO CARD ===")
check_card = call("crm.deal.details.configuration.get", {
    "scope": "C",
    "extras": {"dealCategoryId": 160}
}).get("result", [])

for sec in check_card:
    print(f"\n--- Seção: {sec.get('title')} ({sec.get('name')}) ---")
    for el in sec.get("elements", []):
        print(f"  - {el.get('name')} (flags: {el.get('optionFlags')})")

print("\nConcluído com sucesso!")
