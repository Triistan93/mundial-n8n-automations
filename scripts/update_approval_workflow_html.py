# -*- coding: utf-8 -*-
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
url = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows/uRjdQlM8edLyKmQO'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

wf = requests.get(url, headers=headers).json()

html_code = """
const data = $('Parse_Action_Params').first().json;
const color = data.is_approve ? '#28a745' : '#dc3545';
const title = data.is_approve ? 'Compra Autorizada com Sucesso!' : 'Solicitação de Compra Negada';
const actionEmoji = data.action_emoji;
const statusLabel = data.status_label;
const dealId = data.deal_id;

const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="4;url=https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/">
  <title>${title}</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
    }
    .card {
      background: #ffffff;
      padding: 40px 32px;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.08);
      text-align: center;
      max-width: 480px;
      width: 100%;
    }
    .icon {
      font-size: 50px;
      margin-bottom: 12px;
      line-height: 1;
    }
    .badge {
      display: inline-block;
      padding: 6px 16px;
      border-radius: 20px;
      font-weight: 700;
      color: #ffffff;
      background: ${color};
      font-size: 13px;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
    }
    h1 {
      color: #1a202c;
      font-size: 22px;
      font-weight: 700;
      margin: 0 0 12px 0;
    }
    p {
      color: #4a5568;
      font-size: 15px;
      line-height: 1.6;
      margin: 0 0 20px 0;
    }
    .deal-badge {
      background: #edf2f7;
      padding: 10px 14px;
      border-radius: 8px;
      color: #2d3748;
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 20px;
    }
    .btn-primary {
      display: block;
      padding: 12px 20px;
      background: #007bff;
      color: #ffffff;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      font-size: 15px;
      margin-bottom: 12px;
      transition: background 0.2s;
    }
    .btn-primary:hover {
      background: #0056b3;
    }
    .redirect-timer {
      color: #718096;
      font-size: 13px;
      margin-top: 10px;
    }
  </style>
  <script>
    let seconds = 3;
    function tick() {
      const el = document.getElementById('timer');
      if (el) el.innerText = seconds;
      if (seconds > 0) {
        seconds--;
        setTimeout(tick, 1000);
      } else {
        window.location.href = 'https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/';
      }
    }
    window.onload = tick;
  </script>
</head>
<body>
  <div class="card">
    <div class="icon">${actionEmoji}</div>
    <div class="badge">${statusLabel}</div>
    <h1>${title}</h1>
    <div class="deal-badge">Chamado #${dealId}</div>
    <p>A solicitação de compra foi processada com sucesso no Bitrix24 e a equipe de TI foi notificada.</p>
    <a href="https://b24-88dbfb.bitrix24.com.br/crm/deal/details/${dealId}/" class="btn-primary">Ir para o Chamado no Bitrix24</a>
    <div class="redirect-timer">Redirecionando automaticamente em <strong id="timer">3</strong>s...</div>
  </div>
</body>
</html>`;

return [{
  json: {
    html: html
  }
}];
"""

for n in wf.get('nodes', []):
    if n['name'] == 'Generate_HTML_Response':
        n['parameters']['jsCode'] = html_code

deploy_payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

resp = requests.put(url, headers=headers, json=deploy_payload)
print('Deploy status code:', resp.status_code)
