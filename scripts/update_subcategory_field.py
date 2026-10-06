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

SUBCATEGORY_FIELD_ID = 1678

subcategories_payload = {
    "LIST": [
        # MicroWork Cloud
        {"SORT": "100", "VALUE": "[MicroWork] Emissão de NF / Faturamento"},
        {"SORT": "110", "VALUE": "[MicroWork] Pedido de Vendas / Proposta"},
        {"SORT": "120", "VALUE": "[MicroWork] Estoque / Peças / Transferência"},
        {"SORT": "130", "VALUE": "[MicroWork] Ordem de Serviço (Oficina / Pós-Venda)"},
        {"SORT": "140", "VALUE": "[MicroWork] Sistema Lento ou Travado"},
        {"SORT": "150", "VALUE": "[MicroWork] Erro em Operação / Relatório"},

        # Bitrix24
        {"SORT": "200", "VALUE": "[Bitrix24] Telefonia / Ramal mudo ou não toca"},
        {"SORT": "210", "VALUE": "[Bitrix24] Leads / Negócios / Mensagens sumiram"},
        {"SORT": "220", "VALUE": "[Bitrix24] Lentidão / Tela branca / Erro de login"},
        {"SORT": "230", "VALUE": "[Bitrix24] Chat interno / Mensagens WhatsApp"},

        # RENAVE & ATPV
        {"SORT": "300", "VALUE": "[RENAVE] Intenção de Venda / Comunicação"},
        {"SORT": "310", "VALUE": "[RENAVE] Erro de Integração Detran / SERPRO"},
        {"SORT": "320", "VALUE": "[RENAVE] Consulta / Validação de Chassi"},

        # Portais Honda
        {"SORT": "400", "VALUE": "[Portais Honda] WebPeças - Erro de pedido ou acesso"},
        {"SORT": "410", "VALUE": "[Portais Honda] IHS / FANDI - Erro no portal ou proposta"},

        # Computador & Periféricos
        {"SORT": "500", "VALUE": "[Computador] Não liga / Sem energia"},
        {"SORT": "510", "VALUE": "[Computador] Monitor / Tela preta ou sem sinal"},
        {"SORT": "520", "VALUE": "[Computador] Lentidão extrema / Travamento"},
        {"SORT": "530", "VALUE": "[Computador] Teclado / Mouse / Periféricos"},
        {"ID": "898", "SORT": "540", "VALUE": "[Computador] Manutenção preventiva ou reparo"},

        # Impressora & Scanner
        {"SORT": "600", "VALUE": "[Impressora] Documento travado na fila de impressão"},
        {"SORT": "610", "VALUE": "[Impressora] Impressora Offline ou não encontrada"},
        {"SORT": "620", "VALUE": "[Impressora] Instalação de impressora em nova máquina"},
        {"SORT": "630", "VALUE": "[Impressora] Troca de toner / Falha física / Scanner"},

        # Internet & Rede
        {"SORT": "700", "VALUE": "[Internet/Rede] Queda geral da internet na loja"},
        {"SORT": "710", "VALUE": "[Internet/Rede] Computador sem conexão / Cabo desconectado"},
        {"SORT": "720", "VALUE": "[Internet/Rede] Wi-Fi oscilando ou sem sinal"},

        # Telefonia & Ramais
        {"SORT": "800", "VALUE": "[Telefonia] Headset com defeito / Chiado / Sem áudio"},
        {"SORT": "810", "VALUE": "[Telefonia] Ramal não recebe ou não realiza chamadas"},

        # Acessos & Senhas
        {"ID": "886", "SORT": "900", "VALUE": "[Acessos] Reset de senha / Desbloqueio"},
        {"ID": "884", "SORT": "910", "VALUE": "[Acessos] Novo colaborador / Liberação de acesso"},
        {"SORT": "920", "VALUE": "[Acessos] Desativação de colaborador (Desligamento)"},
        {"SORT": "930", "VALUE": "[Acessos] Liberação de módulo ou permissão especial"},

        # E-mail Corporativo
        {"SORT": "1000", "VALUE": "[E-mail] Não envia ou não recebe e-mails"},
        {"SORT": "1010", "VALUE": "[E-mail] Configuração do Outlook / Webmail"},

        # CFTV / Câmeras
        {"SORT": "1100", "VALUE": "[CFTV/Câmeras] Câmera sem imagem ou gravador offline"},

        # Compras & Geral
        {"ID": "890", "SORT": "1200", "VALUE": "[Compras/TI] Solicitação de novo equipamento ou peça"},
        {"ID": "888", "SORT": "1210", "VALUE": "[Geral] Instalação e configuração de software"},
        {"ID": "906", "SORT": "1220", "VALUE": "[Geral] Erro ou travamento de sistema"},
        {"SORT": "1230", "VALUE": "[Outros] Dúvida operacional ou outro problema"}
    ]
}

print("Atualizando Subcategoria (ID 1678) com Opção A...")
res = call("crm.deal.userfield.update", {
    "id": SUBCATEGORY_FIELD_ID,
    "fields": subcategories_payload
})
print("Resposta:", res)

# Verificar leitura pós-update
uf = call("crm.deal.userfield.get", {"id": SUBCATEGORY_FIELD_ID})
print(f"\nTotal de subcategorias salvas pós-update: {len(uf.get('result', {}).get('LIST', []))}")
for item in uf.get("result", {}).get("LIST", []):
    print(f"  ID={item.get('ID')}, SORT={item.get('SORT')}, VALUE='{item.get('VALUE')}'")
