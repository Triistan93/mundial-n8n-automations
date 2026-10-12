# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. TESTE DO WEBHOOK BITRIX24 DO SDR ===")
b24_url = "https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/crm.dealcategory.list.json"
try:
    r = requests.get(b24_url, timeout=10)
    print("Bitrix Status:", r.status_code)
    if r.status_code == 200:
        cats = r.json().get('result', [])
        print(f"Total de Categorias/Funis no Bitrix: {len(cats)}")
        for c in cats:
            cid = c.get('ID')
            cname = c.get('NAME')
            if str(cid) in ['18', '198', '160', '146', '122', '144', '24']:
                print(f"  -> Categoria ID {cid}: {cname}")
            elif 'sdr' in cname.lower() or 'motos' in cname.lower():
                print(f"  -> Categoria ID {cid}: {cname} (Match SDR/Motos)")
    else:
        print("Erro Bitrix:", r.text[:300])
except Exception as e:
    print("Exceção Bitrix:", e)

print("\n=== 2. TESTE DA INSTÂNCIA EVOLUTION (outrasmidias) ===")
evo_url = "https://sophia-evolution-api.timft8.easypanel.host/instance/connectionState/outrasmidias"
evo_token = "7EuD96NSfnpNRvJZdAAGgnbcdX3rAA9aIsbR8prV7Z0wCyTwQVJdRaEMvj0dgD33KfYtWch6556VSX6JxBMWYC3QHo28CWux9iTqpH5umrnYON2r3DRLzmfyZvrbG2sn"
try:
    r = requests.get(evo_url, headers={'apikey': evo_token}, timeout=10)
    print("Evolution Status:", r.status_code)
    if r.status_code == 200:
        print("Evolution Response:", r.json())
    else:
        print("Erro Evolution:", r.text[:300])
except Exception as e:
    print("Exceção Evolution:", e)
