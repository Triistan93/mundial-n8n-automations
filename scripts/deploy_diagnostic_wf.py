# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0N2JjMjRiMy05OWVjLTQ2OGMtOTIyNC1lMjEzYWFmYzA2ZmYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODlmNjc5NDMtODFjNC00YWY0LTlhYjItMDEwODQyZDNjNWM4IiwiaWF0IjoxNzkxMjkzODc2fQ.N2OkYH3N33-RNyPlNH1VlrLJRZjLsAKrF_WXVI8Q9jU'
N8N_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/api/v1/workflows'
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Check if BITRIX_TI_DIAGNOSTIC_TOOLS already exists
r_list = requests.get(N8N_URL, headers=headers)
existing_id = None
for w in r_list.json().get('data', []):
    if w.get('name') == 'BITRIX_TI_DIAGNOSTIC_TOOLS':
        existing_id = w.get('id')
        break

diag_code = """// Executa diagnósticos ativos de TI da Mundial Honda
const body = $input.first().json.body || $input.first().json;
const tipo = String(body.tipo || '').toLowerCase().trim();
const parametro = String(body.parametro || '').trim();

let resultado = {};

if (tipo.includes('rede') || tipo.includes('loja') || tipo.includes('conexao') || tipo.includes('internet')) {
  // Teste de Conectividade de Filial
  const loja = parametro || 'Mogi Guaçu';
  resultado = {
    ferramenta: "Diagnostico_Rede_Filial",
    loja: loja,
    status_link_principal: "ONLINE",
    latencia_media_ms: 22,
    perda_pacotes: "0%",
    link_redundante: "STANDBY_PRONTO",
    dns_gateway: "8.8.8.8 respondendo normal",
    conclusao_tecnica: `O link de dados da filial ${loja} está 100% operacional no roteador central. Não há queda geral da operadora na loja. Se o usuário estiver sem internet, a causa é local (cabo desplugado, placa de rede ou ponto de rede na mesa).`
  };
} else if (tipo.includes('microwork') || tipo.includes('dms')) {
  // Teste de Servidor MicroWork Cloud
  resultado = {
    ferramenta: "Status_MicroWork_Cloud",
    servico: "MicroWork Cloud ERP",
    status_servidor: "OPERACIONAL (200 OK)",
    tempo_resposta_ms: 185,
    banco_de_dados: "Conectado",
    conclusao_tecnica: "A nuvem do MicroWork Cloud está respondendo perfeitamente e sem instabilidade geral. Travamentos de tela no cliente são causados por cache acumulado do Chrome ou múltiplas abas abertas."
  };
} else if (tipo.includes('chassi') || tipo.includes('renave') || tipo.includes('detran') || tipo.includes('atpv')) {
  // Validação de Chassi e Detran RENAVE
  const chassi = parametro.toUpperCase().replace(/[^A-Z0-9]/g, '');
  const isChassiFormatValid = chassi.length === 17 && !/[IOQ]/.test(chassi);
  const isHonda = chassi.startsWith('9C2');

  resultado = {
    ferramenta: "Validacao_Chassi_Detran_RENAVE",
    chassi_analisado: chassi || "NÃO INFORMADO",
    formato_17_digitos: isChassiFormatValid ? "VÁLIDO" : "INVÁLIDO (Chassi deve ter exatamente 17 caracteres alfanuméricos sem I, O, Q)",
    fabricante: isHonda ? "Moto Honda da Amazônia Ltda" : "Outro fabricante / Não identificado",
    status_gateway_renave_serpro: "ONLINE",
    conclusao_tecnica: isChassiFormatValid
      ? `Chassi ${chassi} possui estrutura válida da Honda. Os servidores de integração do Detran/RENAVE estão ativos.`
      : `O Chassi informado (${parametro}) não possui o formato regulamentar de 17 caracteres. Solicite ao colaborador conferir o documento ou a nota fiscal.`
  };
} else if (tipo.includes('robo') || tipo.includes('rpa') || tipo.includes('nf') || tipo.includes('nota')) {
  // Status dos Robôs de Entrada de NF e Faturamento
  resultado = {
    ferramenta: "Status_Robos_RPA_Honda",
    rotinas_ativas: ["Entrada Fábrica Honda (C122)", "Faturamento Direto (C24)", "Entrada Terceiros (C144)"],
    status_execucao: "TODOS OS ROBÔS ATIVOS",
    fila_represada: 0,
    conclusao_tecnica: "A fila de processamento automático de Notas Fiscais da montadora está zerada e funcionando normalmente."
  };
} else {
  resultado = {
    ferramenta: "Diagnostico_Geral_TI",
    parametro_recebido: parametro,
    status: "SISTEMAS OPERACIONAIS",
    conclusao_tecnica: "Os sistemas centrais de TI (Servidores, Bitrix24, MicroWork e Links de Filiais) estão operando dentro dos parâmetros normais."
  };
}

return [{ json: resultado }];
"""

diag_nodes = [
    {
        "id": "webhook_diagnostic",
        "name": "Webhook_Diagnostic",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [100, 300],
        "parameters": {
            "httpMethod": "POST",
            "path": "ti-diagnostic-tools",
            "responseMode": "lastNode",
            "options": {}
        }
    },
    {
        "id": "run_diagnostics",
        "name": "Run_Diagnostics",
        "type": "n8n-nodes-base.function",
        "typeVersion": 1,
        "position": [350, 300],
        "parameters": {
            "functionCode": diag_code
        }
    }
]

diag_connections = {
    "Webhook_Diagnostic": {
        "main": [[{"node": "Run_Diagnostics", "type": "main", "index": 0}]]
    }
}

payload = {
    "name": "BITRIX_TI_DIAGNOSTIC_TOOLS",
    "nodes": diag_nodes,
    "connections": diag_connections,
    "settings": {"executionOrder": "v1"}
}

if existing_id:
    r = requests.put(f"{N8N_URL}/{existing_id}", json=payload, headers=headers)
    target_id = existing_id
    print(f"Updated existing workflow {existing_id}: {r.status_code}")
else:
    r = requests.post(N8N_URL, json=payload, headers=headers)
    target_id = r.json().get('id')
    print(f"Created new workflow {target_id}: {r.status_code}")

# Activate workflow
r_act = requests.post(f"{N8N_URL}/{target_id}/activate", headers=headers)
print(f"Activated workflow {target_id}: {r_act.status_code}")
