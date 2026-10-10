# -*- coding: utf-8 -*-
import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/testesdr-homolog"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU"

instance_name = f"homolog_s3_{int(time.time())}"

print("=================================================================")
print("  TESTE E2E SPRINT 3: RESGATE DE FOLLOW-UP EM LEAD SILENCIOSO    ")
print("=================================================================\n")

# 1. Enviar mensagem de interesse que deixará o robô em status "andamento"
payload = {
    "apikey": "B4D6E5985D11-498F-B24A-57144CC0BE80",
    "event": "messages.upsert",
    "instance": instance_name,
    "data": {
        "key": {
            "remoteJid": "5519991859143@s.whatsapp.net",
            "fromMe": False,
            "id": f"TEST_S3_{int(time.time())}"
        },
        "pushName": "Eduardo Alaminos",
        "messageType": "conversation",
        "message": {
            "conversation": "Olá, boa tarde! Sou o Eduardo Alaminos e tenho muito interesse em comprar uma Honda Titan 160 Zero KM."
        },
        "messageTimestamp": int(time.time())
    }
}

print(f"URL: {WEBHOOK_URL}")
print(f"Lead: {payload['data']['pushName']} ({payload['data']['key']['remoteJid']})")
print(f"Mensagem enviada: \"{payload['data']['message']['conversation']}\"\n")

t0 = time.time()
r = requests.post(WEBHOOK_URL, json=payload, timeout=30)
print(f"Resposta do Webhook: HTTP {r.status_code}")
print(f"Retorno: {r.text[:200]}")

print("\n--- CRONOGRAMA DO TESTE DE RESGATE ---")
print("1. [0s - 15s]  n8n processa buffer de debounce e chama o AI Agent.")
print("2. [15s - 22s] IA formula a pergunta e dispara para o WhatsApp do lead via 'Continua o Papo'.")
print("3. [22s]       Sprint 3 arma o token e entra no modo de espera (35 segundos).")
print("4. [22s - 57s] O cliente permanece SILENCIOSO (simulando abandono de conversa).")
print("5. [57s - 65s] Wait acorda, valida o token inalterado no Redis e dispara a mensagem de resgate!")

print("\nAguardando 65 segundos para a conclusão de todo o ciclo de resgate...")
for i in range(13):
    time.sleep(5)
    print(f"  ... {(i+1)*5}s decorridos")

print("\n--- CONSULTANDO EXECUÇÕES NO N8N ---")
headers = {"X-N8N-API-KEY": N8N_API_KEY}
r_execs = requests.get("https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions?workflowId=5pFwAtQWvsuhyxO0&limit=3", headers=headers)

if r_execs.status_code == 200:
    execs = r_execs.json().get('data', [])
    for ex in execs:
        ex_id = ex.get('id')
        status = ex.get('status')
        finished = ex.get('finished')
        started = ex.get('startedAt')
        stopped = ex.get('stoppedAt')
        print(f"\n• Execução #{ex_id} | Status: {status} | Finalizada: {finished}")
        print(f"  Início: {started} | Fim: {stopped}")
        
        # Buscar detalhes da execução
        r_det = requests.get(f"https://sophia-n8nsophia.timft8.easypanel.host/api/v1/executions/{ex_id}?includeData=true", headers=headers)
        if r_det.status_code == 200:
            run_data = r_det.json().get('data', {}).get('resultData', {}).get('runData', {})
            executed_nodes = list(run_data.keys())
            print(f"  Nós executados ({len(executed_nodes)}): {executed_nodes[-6:]}")
            
            if 'Avaliar Disparo do Resgate (Sprint 3)' in run_data:
                out = run_data['Avaliar Disparo do Resgate (Sprint 3)'][0].get('data', {}).get('main', [[{}]])[0][0].get('json', {})
                print(f"  ✅ Decisão do Resgate: deve_resgatar = {out.get('deve_resgatar')}")
                print(f"  💬 Mensagem de Resgate Formulada:\n  \"{out.get('mensagem_resgate')}\"")
            if 'Enviar MSG Resgate (WhatsApp)' in run_data:
                print("  📲 Disparo no WhatsApp da Evolution API: EXECUTADO COM SUCESSO!")
            if 'Inserir Resgate na Memoria IA' in run_data:
                print("  🧠 Registro na Memória LangChain: SINCRONIZADO COM SUCESSO!")
            break
else:
    print("Erro ao consultar execuções:", r_execs.text)
