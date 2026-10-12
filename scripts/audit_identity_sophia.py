# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("  AUDITORIA DE IDENTIDADE: SOPHIA (244936) vs DEV BOT (61622)   ")
print("=================================================================\n")

# 1. Checagem no SDR
with open('c:/mundial-n8n-automations/workflows/SDR_Mundial_Motos_Unificado.json', 'r', encoding='utf-8') as f:
    sdr_wf = json.load(f)

print("--- 1. NÓS DO SDR COM INTEGRAÇÃO BITRIX ---")
sdr_nodes = sdr_wf.get('nodes', [])
for n in sdr_nodes:
    node_str = json.dumps(n, ensure_ascii=False)
    if 'bitrix24.com.br' in node_str or '61622' in node_str or '244936' in node_str:
        has_sophia = '244936' in node_str
        has_devbot = '61622' in node_str
        identity = "SOPHIA (244936)" if has_sophia else ("DEV BOT (61622)" if has_devbot else "OUTRO")
        if has_sophia and has_devbot:
            identity = "AMBOS (!)"
        print(f"• Nó: '{n['name']}' ({n['type']}) -> Identidade: {identity}")
        
        # Check URLs in parameters
        params = n.get('parameters', {})
        url = params.get('url', '')
        if url:
            print(f"    URL: {url}")
        js_code = params.get('jsCode', '')
        if 'bitrix' in js_code:
            for line in js_code.split('\n'):
                if 'bitrix24' in line or 'rest/' in line:
                    print(f"    Code line: {line.strip()}")

# 2. Checagem no RH
print("\n--- 2. NÓS DO RH COM INTEGRAÇÃO BITRIX ---")
with open('c:/mundial-n8n-automations/workflows/AGENTE_RH_COM_CORRECOES_8OvNSMmZFZWxiW9A.json', 'r', encoding='utf-8') as f:
    rh_wf = json.load(f)

rh_nodes = rh_wf.get('nodes', [])
for n in rh_nodes:
    node_str = json.dumps(n, ensure_ascii=False)
    if 'bitrix24.com.br' in node_str or '61622' in node_str or '244936' in node_str:
        has_sophia = '244936' in node_str
        has_devbot = '61622' in node_str
        identity = "SOPHIA (244936)" if has_sophia else ("DEV BOT (61622)" if has_devbot else "OUTRO")
        if has_sophia and has_devbot:
            identity = "AMBOS (!)"
        print(f"• Nó: '{n['name']}' ({n['type']}) -> Identidade: {identity}")
        params = n.get('parameters', {})
        url = params.get('url', '')
        if url:
            print(f"    URL: {url}")
