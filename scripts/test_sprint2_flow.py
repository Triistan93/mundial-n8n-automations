import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/'

def call_b24(method, payload):
    url = f"{webhook}{method}.json"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=== TESTANDO CRIAÇÃO DE DEAL EM ASSUNTOS RH E ALERTA IM ===")

# 1. Simular dados de transferência
tipo_label = "🏥 Saúde Ocupacional / Clínica / Exames"
nome = "Dr. Roberto (Clínica São Camilo)"
telefone = "5519999998888"
resumo = "Envio de ASO admissional do candidato João Silva"
assigned_id = 32598  # Eduardo Alaminos para teste

# 2. Criar Deal na etapa C198:UC_0YLZXN (ASSUNTOS RH)
deal_payload = {
    "fields": {
        "TITLE": f"[RH - {tipo_label}] {nome}",
        "CATEGORY_ID": 198,
        "STAGE_ID": "C198:UC_0YLZXN",
        "ASSIGNED_BY_ID": assigned_id,
        "COMMENTS": f"<b>Demanda recebida via WhatsApp (Bot RH):</b><br>Tipo: {tipo_label}<br>Solicitante: {nome}<br>Telefone: {telefone}<br>Resumo: {resumo}"
    }
}
deal_res = call_b24("crm.deal.add", deal_payload)
deal_id = deal_res.get("result")
print(f"✅ Deal criado com sucesso! ID: {deal_id}")

# 3. Adicionar Comentário na Timeline
timeline_payload = {
    "fields": {
        "ENTITY_ID": deal_id,
        "ENTITY_TYPE": "deal",
        "COMMENT": f"<b>⚠️ TRANSFERÊNCIA HUMANA / ATENDIMENTO RH:</b><br><b>Tipo:</b> {tipo_label}<br><b>Solicitante:</b> {nome}<br><b>Telefone:</b> {telefone}<br><b>Resumo:</b> {resumo}<br><i>O robô foi pausado para permitir o atendimento humano no WhatsApp.</i>"
    }
}
timeline_res = call_b24("crm.timeline.comment.add", timeline_payload)
print(f"✅ Timeline registrada! ID: {timeline_res.get('result')}")

# 4. Enviar Alerta no Chat Privado para Eduardo (32598)
alert_message = (
    f"🔔 [ALERTA RH - TESTE] Novo Atendimento no WhatsApp aguardando equipe!\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"📌 Tipo: {tipo_label}\n"
    f"👤 Solicitante: {nome}\n"
    f"📱 WhatsApp: {telefone}\n"
    f"📝 Resumo: {resumo}\n"
    f"🔗 Abrir Card no Bitrix: https://b24-88dbfb.bitrix24.com.br/crm/deal/details/{deal_id}/\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)
msg_payload = {
    "DIALOG_ID": assigned_id,
    "MESSAGE": alert_message
}
msg_res = call_b24("im.message.add", msg_payload)
print(f"✅ Mensagem de alerta enviada no chat para Eduardo (32598)! Msg ID: {msg_res.get('result')}")
