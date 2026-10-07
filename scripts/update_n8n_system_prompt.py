# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG'

headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

print("Buscando workflow atual no n8n...")
resp = requests.get(N8N_URL, headers=headers)
wf = resp.json()

old_sec7 = "7. PORTAIS HONDA: WEBPEÇAS, IHS & FANDI (KB-014):"
new_sec7 = """7. PORTAIS HONDA (WEBPEÇAS & IHS) E PLATAFORMA FANDI (KB-014):
   - Plataforma FANDI: É uma ferramenta de propostas, simulações e financiamentos (NÃO é um portal Honda). Se houver erro de simulação ou proposta travada, colete o número da proposta/simulação e mensagem de erro exibida.
   - WebPeças (Portal Honda de Peças): Erro de 'Sua conexão não é particular / Site não seguro': Oriente a clicar em 'Avançado' e depois em 'Continuar para o site (não seguro)' ou testar abrir pelo Microsoft Edge.
   - WebPeças: Catálogo de peças não carrega ou botões não respondem: Oriente a liberar Pop-ups bloqueados no canto direito da barra de endereço do navegador."""

old_sec8_part = "Sistema (MicroWork, Bitrix24, E-mail ou Portal Honda)"
new_sec8_part = "Sistema (MicroWork, Bitrix24, E-mail, Portal Honda ou FANDI)"

old_sec9 = """9. E-MAIL CORPORATIVO & OUTLOOK (KB-008):
   - E-mail não envia ou fica preso na caixa de saída: Checar se o arquivo anexo é muito grande ou se o Outlook está em 'Trabalhar Offline'.
   - E-mail não abre: Testar o acesso via Webmail no navegador."""

new_sec9 = """9. E-MAIL CORPORATIVO & OUTLOOK (KB-008):
   - Domínios corporativos oficiais da rede: @mundialmotos e @mundialhonda.
   - E-mail não envia ou fica preso na caixa de saída: Checar se o arquivo anexo é muito grande ou se o Outlook está em 'Trabalhar Offline'.
   - E-mail não abre: Testar o acesso via Webmail no navegador."""

updated = False
for node in wf.get('nodes', []):
    if node.get('name') == '08_AI_Agent_Triage_Deal':
        sm = node['parameters']['options']['systemMessage']
        if old_sec7 in sm:
            # Replace old sec 7 block
            end_sec7 = sm.find('8. ACESSOS')
            start_sec7 = sm.find(old_sec7)
            sm = sm[:start_sec7] + new_sec7 + "\n\n" + sm[end_sec7:]
            print("Seção 7 substituída com sucesso.")
            
        if old_sec8_part in sm:
            sm = sm.replace(old_sec8_part, new_sec8_part)
            print("Seção 8 ajustada para incluir FANDI.")
            
        if old_sec9 in sm:
            sm = sm.replace(old_sec9, new_sec9)
            print("Seção 9 substituída com domínios @mundialmotos e @mundialhonda.")
            
        node['parameters']['options']['systemMessage'] = sm
        updated = True
        break

if not updated:
    print("ERRO: Nó 08_AI_Agent_Triage_Deal não encontrado ou textos não bateram.")
    sys.exit(1)

# Save to local canonical file first
canonical_path = r"C:\mundial-n8n-automations\workflows\canonical\BITRIX_TI_AI_TRIAGE_AGENT.json"
with open(canonical_path, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print(f"Salvo arquivo canônico local em {canonical_path}")

# Deploy to n8n
deploy_payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

put_resp = requests.put(N8N_URL, headers=headers, json=deploy_payload)
print(f"Status do PUT no n8n: {put_resp.status_code}")
if put_resp.status_code == 200:
    print("Workflow n8n atualizado com sucesso!")
else:
    print(f"Erro na resposta do n8n: {put_resp.text}")
