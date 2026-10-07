# -*- coding: utf-8 -*-
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

# 1. Update Categoria (1676)
# - FANDI without Honda prefix
# - E-mail Corporativo (@mundialmotos / @mundialhonda)
# - Ensure SETTINGS LIST_HEIGHT is 1
cat_payload = {
    "SETTINGS": {
        "DISPLAY": "LIST",
        "LIST_HEIGHT": 1,
        "CAPTION_NO_VALUE": "",
        "SHOW_NO_VALUE": "Y"
    },
    "LIST": [
        {"ID": "878", "SORT": "10", "VALUE": "MicroWork Cloud (DMS/ERP)"},
        {"ID": "874", "SORT": "20", "VALUE": "Bitrix24 (CRM / Leads / Chat)"},
        {"ID": "908", "SORT": "30", "VALUE": "RENAVE & ATPV"},
        {"ID": "868", "SORT": "40", "VALUE": "Portais Honda: IHS Motocicletas"},
        {"ID": "870", "SORT": "50", "VALUE": "Portais Honda: IHS Financeiro"},
        {"ID": "914", "SORT": "60", "VALUE": "Portais Honda: WebPeças"},
        {"ID": "872", "SORT": "70", "VALUE": "Portais Honda: Vendas Digital"},
        {"ID": "902", "SORT": "80", "VALUE": "FANDI"},
        {"ID": "880", "SORT": "90", "VALUE": "Computador & Monitor"},
        {"ID": "882", "SORT": "100", "VALUE": "Impressora & Scanner"},
        {"ID": "920", "SORT": "110", "VALUE": "Câmeras (CFTV)"},
        {"ID": "916", "SORT": "120", "VALUE": "E-mail Corporativo (@mundialmotos / @mundialhonda)"},
        {"ID": "918", "SORT": "130", "VALUE": "Acessos, Senhas & Contas"},
        {"ID": "876", "SORT": "140", "VALUE": "Solicitação de Compra de TI"},
        {"ID": "904", "SORT": "150", "VALUE": "Pacote Office / Softwares"},
        {"ID": "1214", "SORT": "160", "VALUE": "Internet & Rede da Loja (Cabo / Wi-Fi)"},
        {"ID": "1216", "SORT": "170", "VALUE": "Telefonia & Ramais (Headset / Ligações)"},
        {"ID": "1218", "SORT": "180", "VALUE": "Outros Assuntos de TI"}
    ]
}

print("Aplicando correções em Categoria (ID 1676)...")
res_cat = call("crm.deal.userfield.update", {
    "id": 1676,
    "fields": cat_payload
})
print("Resultado Categoria:", res_cat)

# 2. Update Subcategoria (1678)
# - Item 1248: Portais Honda: IHS Motocicletas / IHS Financeiro - Erro no portal
# - New Item or separate: [FANDI] Erro no sistema / Proposta / Simulação
sub_payload = {
    "SETTINGS": {
        "DISPLAY": "LIST",
        "LIST_HEIGHT": 1,
        "CAPTION_NO_VALUE": "",
        "SHOW_NO_VALUE": "Y"
    },
    "LIST": [
        {"ID": "1248", "SORT": "410", "VALUE": "[Portais Honda] IHS Motocicletas / IHS Financeiro - Erro no portal"},
        {"SORT": "420", "VALUE": "[FANDI] Erro no sistema / Proposta / Simulação"}
    ]
}

print("Aplicando correções em Subcategoria (ID 1678)...")
res_sub = call("crm.deal.userfield.update", {
    "id": 1678,
    "fields": sub_payload
})
print("Resultado Subcategoria:", res_sub)

# 3. Validar leitura de ambos os campos
print("\n" + "="*60)
print("VALIDAÇÃO FINAL - CATEGORIA (1676)")
print("="*60)
cat_check = call("crm.deal.userfield.get", {"id": 1676}).get("result", {})
print(f"LIST_HEIGHT: {cat_check.get('SETTINGS', {}).get('LIST_HEIGHT')}")
for c in cat_check.get("LIST", []):
    print(f"  ID={c.get('ID')}, SORT={c.get('SORT')}, VALUE='{c.get('VALUE')}'")

print("\n" + "="*60)
print("VALIDAÇÃO FINAL - SUBCATEGORIA (1678)")
print("="*60)
sub_check = call("crm.deal.userfield.get", {"id": 1678}).get("result", {})
print(f"LIST_HEIGHT: {sub_check.get('SETTINGS', {}).get('LIST_HEIGHT')}")
for s in sub_check.get("LIST", []):
    if "Honda" in s.get("VALUE", "") or "FANDI" in s.get("VALUE", ""):
        print(f"  ID={s.get('ID')}, SORT={s.get('SORT')}, VALUE='{s.get('VALUE')}'")
