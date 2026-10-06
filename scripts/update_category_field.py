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

CATEGORY_FIELD_ID = 1676

categories_payload = {
    "LIST": [
        {"ID": "878", "SORT": "10", "VALUE": "MicroWork Cloud (DMS/ERP)"},
        {"ID": "874", "SORT": "20", "VALUE": "Bitrix24 (CRM / Leads / Chat)"},
        {"ID": "908", "SORT": "30", "VALUE": "RENAVE & ATPV"},
        {"ID": "868", "SORT": "40", "VALUE": "Portais Honda: IHS Motocicletas"},
        {"ID": "870", "SORT": "50", "VALUE": "Portais Honda: IHS Financeiro"},
        {"ID": "902", "SORT": "60", "VALUE": "Portais Honda: FANDI"},
        {"ID": "914", "SORT": "70", "VALUE": "Portais Honda: WebPeças"},
        {"ID": "872", "SORT": "80", "VALUE": "Portais Honda: Vendas Digital"},
        {"ID": "880", "SORT": "90", "VALUE": "Computador & Monitor"},
        {"ID": "882", "SORT": "100", "VALUE": "Impressora & Scanner"},
        {"ID": "920", "SORT": "110", "VALUE": "Câmeras (CFTV)"},
        {"ID": "916", "SORT": "120", "VALUE": "E-mail Corporativo (@mundialmotos)"},
        {"ID": "918", "SORT": "130", "VALUE": "Acessos, Senhas & Contas"},
        {"ID": "876", "SORT": "140", "VALUE": "Solicitação de Compra de TI"},
        {"ID": "904", "SORT": "150", "VALUE": "Pacote Office / Softwares"},
        {"SORT": "160", "VALUE": "Internet & Rede da Loja (Cabo / Wi-Fi)"},
        {"SORT": "170", "VALUE": "Telefonia & Ramais (Headset / Ligações)"},
        {"SORT": "180", "VALUE": "Outros Assuntos de TI"}
    ]
}

print("Atualizando Categoria (ID 1676)...")
res = call("crm.deal.userfield.update", {
    "id": CATEGORY_FIELD_ID,
    "fields": categories_payload
})
print("Resposta:", res)

# Verificar leitura
uf = call("crm.deal.userfield.get", {"id": CATEGORY_FIELD_ID})
print("\nOpções salvas pós-update:")
for item in uf.get("result", {}).get("LIST", []):
    print(f"  ID={item.get('ID')}, SORT={item.get('SORT')}, VALUE='{item.get('VALUE')}'")
