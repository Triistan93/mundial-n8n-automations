# -*- coding: utf-8 -*-
"""
Criação do Workflow de Botão de Pânico (Fail-Safe Kill Switch)
Cria um workflow independente no n8n:
- Webhook GET: /webhook/panic-ti-stop -> Desativa o agente de triagem c0F2GUMFm2BI94UG imediatamente
- Webhook GET: /webhook/panic-ti-resume -> Reativa o agente de triagem c0F2GUMFm2BI94UG
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# 1. Checa se o workflow de pânico já existe
r_list = requests.get('https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows', headers=headers)
existing_id = None
for wf in r_list.json().get('data', []):
    if wf['name'] == 'TI_PANIC_BUTTON_HANDLER':
        existing_id = wf['id']
        break

payload = {
    'name': 'TI_PANIC_BUTTON_HANDLER',
    'nodes': [
        {
            'name': 'Webhook_Panic_Stop',
            'type': 'n8n-nodes-base.webhook',
            'typeVersion': 2,
            'position': [200, 300],
            'parameters': {
                'httpMethod': 'GET',
                'path': 'panic-ti-stop',
                'responseMode': 'responseNode',
                'options': {}
            }
        },
        {
            'name': 'Deactivate_Triage_Workflow',
            'type': 'n8n-nodes-base.httpRequest',
            'typeVersion': 4.2,
            'position': [440, 300],
            'parameters': {
                'method': 'POST',
                'url': 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG/deactivate',
                'sendHeaders': True,
                'headerParameters': {
                    'parameters': [
                        { 'name': 'X-N8N-API-KEY', 'value': API_KEY }
                    ]
                },
                'options': {}
            }
        },
        {
            'name': 'Respond_Panic_Triggered',
            'type': 'n8n-nodes-base.respondToWebhook',
            'typeVersion': 1.1,
            'position': [680, 300],
            'parameters': {
                'respondWith': 'text',
                'responseBody': '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Botao de Panico TI</title></head><body style="font-family:Segoe UI,sans-serif;text-align:center;padding:50px 20px;background:#fff5f5;"><div style="max-width:600px;margin:0 auto;background:white;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:6px solid #d32f2f;"><h1 style="color:#d32f2f;margin-top:0;">🚨 BOTAO DE PANICO ACIONADO!</h1><p style="font-size:18px;color:#333;line-height:1.6;">O Agente Sophia de triagem de tickets da Central de TI (<b>c0F2GUMFm2BI94UG</b>) foi <b>PARALISADO IMEDIATAMENTE</b>.</p><p style="color:#666;font-size:15px;">Nenhum novo ticket recebera mensagem automatica ou sera processado.</p><div style="margin-top:30px;"><a href="/webhook/panic-ti-resume" style="display:inline-block;padding:14px 28px;background:#2e7d32;color:white;text-decoration:none;border-radius:8px;font-weight:bold;font-size:16px;">▶️ Reativar Agente Sophia</a></div></div></body></html>',
                'options': {
                    'responseHeaders': {
                        'entries': [
                            { 'name': 'Content-Type', 'value': 'text/html; charset=utf-8' }
                        ]
                    }
                }
            }
        },
        {
            'name': 'Webhook_Panic_Resume',
            'type': 'n8n-nodes-base.webhook',
            'typeVersion': 2,
            'position': [200, 520],
            'parameters': {
                'httpMethod': 'GET',
                'path': 'panic-ti-resume',
                'responseMode': 'responseNode',
                'options': {}
            }
        },
        {
            'name': 'Activate_Triage_Workflow',
            'type': 'n8n-nodes-base.httpRequest',
            'typeVersion': 4.2,
            'position': [440, 520],
            'parameters': {
                'method': 'POST',
                'url': 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/c0F2GUMFm2BI94UG/activate',
                'sendHeaders': True,
                'headerParameters': {
                    'parameters': [
                        { 'name': 'X-N8N-API-KEY', 'value': API_KEY }
                    ]
                },
                'options': {}
            }
        },
        {
            'name': 'Respond_Panic_Resumed',
            'type': 'n8n-nodes-base.respondToWebhook',
            'typeVersion': 1.1,
            'position': [680, 520],
            'parameters': {
                'respondWith': 'text',
                'responseBody': '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Sophia Reativada</title></head><body style="font-family:Segoe UI,sans-serif;text-align:center;padding:50px 20px;background:#f5fff5;"><div style="max-width:600px;margin:0 auto;background:white;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:6px solid #2e7d32;"><h1 style="color:#2e7d32;margin-top:0;">✅ AGENTE SOPHIA REATIVADO!</h1><p style="font-size:18px;color:#333;line-height:1.6;">O workflow de triagem da Central de TI esta <b>ATIVO E OPERANDO</b> novamente.</p><div style="margin-top:30px;"><a href="/webhook/panic-ti-stop" style="display:inline-block;padding:14px 28px;background:#d32f2f;color:white;text-decoration:none;border-radius:8px;font-weight:bold;font-size:16px;">🚨 Botao de Panico (Parar Imediatamente)</a></div></div></body></html>',
                'options': {
                    'responseHeaders': {
                        'entries': [
                            { 'name': 'Content-Type', 'value': 'text/html; charset=utf-8' }
                        ]
                    }
                }
            }
        }
    ],
    'connections': {
        'Webhook_Panic_Stop': {
            'main': [
                [{ 'node': 'Deactivate_Triage_Workflow', 'type': 'main', 'index': 0 }]
            ]
        },
        'Deactivate_Triage_Workflow': {
            'main': [
                [{ 'node': 'Respond_Panic_Triggered', 'type': 'main', 'index': 0 }]
            ]
        },
        'Webhook_Panic_Resume': {
            'main': [
                [{ 'node': 'Activate_Triage_Workflow', 'type': 'main', 'index': 0 }]
            ]
        },
        'Activate_Triage_Workflow': {
            'main': [
                [{ 'node': 'Respond_Panic_Resumed', 'type': 'main', 'index': 0 }]
            ]
        }
    },
    'settings': {
        'executionOrder': 'v1'
    }
}

if existing_id:
    print(f"Atualizando workflow existente {existing_id}...")
    r = requests.put(f'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/{existing_id}', headers=headers, json=payload)
    wf_id = existing_id
else:
    print("Criando novo workflow de pânico...")
    r = requests.post('https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows', headers=headers, json=payload)
    wf_id = r.json().get('id')

print(f"Workflow ID: {wf_id} (Status: {r.status_code})")

# Ativa o workflow de pânico
r_act = requests.post(f'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/{wf_id}/activate', headers=headers)
print(f"Status da ativacao do Panic Workflow: {r_act.status_code}")
print("Urls de controle:")
print("  STOP:   https://sophia-n8nsophia.timft8.easypanel.host/webhook/panic-ti-stop")
print("  RESUME: https://sophia-n8nsophia.timft8.easypanel.host/webhook/panic-ti-resume")
