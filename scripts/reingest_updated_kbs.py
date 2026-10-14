# -*- coding: utf-8 -*-
"""
Script de Reingestão das Bases de Conhecimento Refinadas no pgvector (kb_ti_conhecimento)
Atualiza KB-013 (RENAVE/ATPV), KB-005 (Senhas/Autoatendimento), KB-015 (WhatsApp/Fale Fácil)
e insere KB-016 (Onboarding e Acessos de Novos Colaboradores).
"""
import requests
import json
import time

N8N_SQL_URL = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
INGEST_WEBHOOK = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-ingest'

print("1. Removendo chunks legados das KBs 005, 013, 015 e 016 no PostgreSQL...")
del_sql = "DELETE FROM kb_ti_conhecimento WHERE metadata->>'kb_id' IN ('KB-013', 'KB-005', 'KB-015', 'KB-016');"
r_del = requests.post(N8N_SQL_URL, json={'query': del_sql})
print("Resultado da limpeza:", r_del.json())

# Artigos completos enriquecidos
docs = [
    {
        "kb_id": "KB-013",
        "title": "RENAVE e ATPV: Intenção de Venda, Transferência e Validação de Chassi",
        "systems": "RENAVE, ATPV-e, MicroWork Cloud, Detran / Serpro",
        "keywords": "renave, atpv, atpv-e, intenção de venda, gerar intenção, transferência, chassi, 9c2, erro renave, erro atpv, detran, documento veículo, venda de moto, erro de comunicação detran, transferência entre lojas, cliente final, f&i, nataelen, camily",
        "source": "KB-013-renave-atpv-intencao-venda.md",
        "text": """# KB-013 - RENAVE e ATPV: Intenção de Venda, Transferência e Validação de Chassi
Sistemas: RENAVE, ATPV-e, MicroWork Cloud, Detran / Serpro
Palavras-chave: renave, atpv, atpv-e, intenção de venda, gerar intenção, transferência, chassi, 9c2, erro renave, erro atpv, detran, documento veículo, venda de moto, erro de comunicação detran, transferência entre lojas, cliente final, f&i, nataelen, camily

## Quando usar
O colaborador do F&I ou vendas relata: "preciso gerar ATPV", "erro no Renave ao tentar gerar a intenção de venda", "ATPV com erro", "o Detran rejeitou os dados do veículo".

## Regra de Ouro da Triagem L1 (Diferenciação Obrigatória)
Antes de escalar o chamado para a equipe de TI, o assistente DEVE OBRIGATORIAMENTE verificar a finalidade da operação:
1. **Transferência entre Lojas Internas da Rede Mundial:**
   - A equipe de TI **NÃO** emite ATPV para transferências internas entre concessionárias da rede!
   - Orientação L1: Informar com gentileza ao colaborador que transferências entre lojas são tratadas diretamente pela rotina interna de movimentação de estoque de veículos e não requerem geração de ATPV pela TI.
2. **Venda para Cliente Final (Pessoa Física ou Jurídica):**
   - Esta sim exige a emissão da ATPV-e / Intenção de Venda pelo suporte de TI.

## Dados Obrigatórios para Emissão da ATPV (Venda Final)
Para que a equipe de TI execute a emissão no MicroWork Cloud DMS, colete obrigatoriamente:
1. **Chassi Completo da Motocicleta:**
   - Deve conter exatamente 17 caracteres alfanuméricos, iniciando obrigatoriamente por **`9C2...`** (ex: `9C2KC...`, `9C2JB...`).
2. **Print ou Mensagem de Erro em Tela:**
   - O print da tela do MicroWork com o código ou descrição do erro exibido ao tentar gerar (lido pelo GPT-4o Vision).

## Procedimento Técnico de Resolução da Equipe de TI
O técnico de suporte executa a seguinte rotina oficial:
1. Acessa a rotina do MicroWork Cloud DMS:
   **Link Direto:** `https://microworkcloud.com.br/cloud/#/veiculo/estoque/renave`
2. Filtra pelo Chassi informado;
3. No campo Período, define como **`PERÍODO`**;
4. Desmarca a caixa de seleção **`NOVO`**;
5. Seleciona a **Filial / Concessionária** correspondente;
6. Clica em **Busca** e conclui a transmissão da intenção de venda/ATPV."""
    },
    {
        "kb_id": "KB-005",
        "title": "Senha expirada, bloqueada ou redefinição de acesso (Autoatendimento L1)",
        "systems": "Bitrix24, MicroWork Cloud, FANDI, IHS Honda, Windows / Rede",
        "keywords": "senha, reset de senha, esqueci minha senha, desbloqueio, conta bloqueada, login, recuperar senha, bitrix24, microwork cloud, fandi, ihs, e-mail corporativo",
        "source": "KB-005-senhas-e-acessos-autoatendimento.md",
        "text": """# KB-005 - Senha expirada, bloqueada ou redefinição de acesso (Autoatendimento L1)
Sistemas: Bitrix24, MicroWork Cloud, Plataforma FANDI, IHS Motocicletas, Windows / Rede
Palavras-chave: senha, reset de senha, esqueci minha senha, desbloqueio, conta bloqueada, login, recuperar senha, bitrix24, microwork cloud, fandi, ihs, e-mail corporativo

## 1. Fluxo de Autoatendimento L1 (Resolução Direta pelo Usuário)
Os seguintes sistemas possuem funcionalidade nativa de auto-recuperação que envia o link de redefinição diretamente para o e-mail corporativo do colaborador:
- **Bitrix24 CRM**
- **MicroWork Cloud DMS**
- **Plataforma FANDI (Simulador)**

### Roteiro de Orientação da Sophia AI (L1):
Ao receber um pedido de redefinição de senha para esses 3 sistemas, o assistente orienta:
> "Antes de abrirmos um chamado para a equipe técnica, você pode usar a opção **'Esqueci minha senha'** na tela inicial de login do [Bitrix/Cloud/Fandi]. O sistema enviará um link de redefinição diretamente para a sua caixa de entrada do e-mail corporativo. Você já chegou a verificar seu e-mail corporativo com essa opção?"

- Se o colaborador conseguir redefinir: O chamado é concluído como **`RESOLVED_L1`** com sucesso imediato sem fila!
- Se o colaborador declarar que não possui acesso ao e-mail corporativo ou que a conta foi bloqueada por excesso de tentativas: Conclua a triagem e encaminhe para a TI.

## 2. Sistemas com Redefinição Manual Obrigatória pela TI (L2)
Os seguintes sistemas exigem intervenção manual direta do suporte técnico no painel de administração:
- **IHS Motocicleta (Portal da Montadora Honda):** Acesso à extranet Honda gerenciado manualmente pela TI.
- **Windows / Rede Corporativa / Active Directory:** Desbloqueio de usuário ou reset de senha de máquina física.
- **VPN / Conexão Segura:** Reset de credenciais de acesso remoto."""
    },
    {
        "kb_id": "KB-015",
        "title": "WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil",
        "systems": "WhatsApp Corporativo, Bitrix24 Contact Center, Plataforma Fale Fácil, Meta WhatsApp Business",
        "keywords": "whatsapp, wpp, fale facil, contact center, espelhamento, canal desconectado, qr code, qrcode, ler qr code, mensagens não chegam, não envia mensagem, número banido, tudo vermelho, canal individual, f&i doc, linha corporativa, desconectou do bitrix, mensagens atrasadas, template bitrix, link de cliente de exemplo",
        "source": "KB-015-whatsapp-corporativo-fale-facil.md",
        "text": """# KB-015 - WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil
Sistemas: WhatsApp Corporativo, Bitrix24 Contact Center, Plataforma Fale Fácil, Meta WhatsApp Business
Palavras-chave: whatsapp, wpp, fale facil, contact center, espelhamento, canal desconectado, qr code, qrcode, ler qr code, mensagens não chegam, não envia mensagem, número banido, tudo vermelho, canal individual, f&i doc, linha corporativa, desconectou do bitrix, mensagens atrasadas, template bitrix, link de cliente de exemplo

## Quando usar
O colaborador relata: "mensagens não chegam", "meu WhatsApp não espelha no Bitrix", "canal individual desconectou", "precisa de novo QR Code", "número do F&I não envia mensagem".

## Escopo do Bot & Coleta Obrigatória para a TI
O colaborador NÃO tem acesso à plataforma Fale Fácil e não deve ser orientado a mexer nela. O bot deve coletar:
1. **Número Corporativo / Ramal Afetado:** Número com DDD (ex: 19 9xxxx-xxxx ou ramal da loja).
2. **Evidências Técnicas Mandatórias (Uma das duas opções):**
   - **Print da Tela de Erro:** Imagem capturada da tela mostrando o erro (analisada pelo GPT-4o Vision);
   - **Link de um Card/Cliente de Exemplo no Bitrix24:** Se o erro for "não está indo mensagem para o cliente", pedir o link de um card de atendimento recente para que a TI possa rastrear os logs no servidor.
3. **Checagem Guiada no Smartphone Físico:**
   - Solicitar que o colaborador olhe em: *Configurações > Dispositivos Conectados* do WhatsApp no aparelho e informe se aparece como 'Conectado' ou 'Desconectado'.

## Ação da Equipe Técnica de TI
A equipe entra no console da Fale Fácil / Bitrix Openlines, reinicia a sessão da instância, gera o novo QR Code caso necessário e aciona o colaborador para leitura ou normalização."""
    },
    {
        "kb_id": "KB-016",
        "title": "Onboarding e Liberação de Acessos para Novos Colaboradores",
        "systems": "MicroWork Cloud, Bitrix24, Telefonia Fale Fácil, IHS Honda, FANDI, Hardware",
        "keywords": "novo colaborador, novo vendedor, contratação, liberar acessos, admissão, onboarding, criar usuário, cadastrar vendedor, fila de atendimento, ramal novo, computador para novo funcionário, celeste, silvana, paula brenda, karina",
        "source": "KB-016-onboarding-liberacao-acessos.md",
        "text": """# KB-016 - Onboarding e Liberação de Acessos para Novos Colaboradores
Sistemas: MicroWork Cloud, Bitrix24 CRM, Telefonia Fale Fácil, IHS Honda, Plataforma FANDI
Palavras-chave: novo colaborador, novo vendedor, contratação, liberar acessos, admissão, onboarding, criar usuário, cadastrar vendedor, fila de atendimento, ramal novo, computador para novo funcionário, celeste, silvana, paula brenda, karina

## Quando usar
Gerentes de Loja (Celeste, Silvana, Anderson, Andréia) ou Supervisoras (Paula Brenda, Karina Volsi) solicitam criação ou liberação de acessos para um novo consultor ou funcionário na concessionária.

## Checklist Obrigatório que o Assistente Sophia AI deve Extrair do Gestor:
Para que a TI execute a criação dos acessos sem retrabalho ou trocas de mensagens adicionais, colete:
1. **Nome Completo e Função / Cargo:** Qual a função exata do novo colaborador (ex: Consultor de Vendas Novas, Vendas Seminovas, Caixa, Faturista, Balconista de Peças, Consultor Técnico)?
2. **Telefonia & Fila de Atendimento:**
   - O colaborador precisará de ramal de telefonia ativa (Fale Fácil)?
   - Se sim, em **qual fila de atendimento** ele deve ser inserido (ex: Vendas Araras, F&I Hortolândia, Pós-Vendas Campinas)?
3. **Canal de WhatsApp:**
   - O colaborador utilizará o WhatsApp oficial coletivo da loja ou terá um canal individual de atendimento?
4. **Disponibilidade de Equipamentos (Hardware):**
   - O setor/loja já possui máquina física (computador, monitor, headset) disponível para uso, ou já foi solicitada a compra de equipamento?

Com essas 4 respostas, o chamado é estruturado perfeitamente na Categoria 160 para criação em lote de acessos."""
    }
]

print("\n2. Enviando documentos enriquecidos para o webhook de ingestão do n8n...")
payload = {"documents": docs}
r_ingest = requests.post(INGEST_WEBHOOK, json=payload)
print(f"Status da ingestão: {r_ingest.status_code} - {r_ingest.text}")

print("\n3. Aguardando 5 segundos para indexação vetorial...")
time.sleep(5)

print("\n4. Verificando artigos presentes em kb_ti_conhecimento após ingestão...")
r_check = requests.post(N8N_SQL_URL, json={'query': "SELECT DISTINCT metadata->>'kb_id' as kb_id, metadata->>'title' as title FROM kb_ti_conhecimento ORDER BY kb_id ASC;"})
rows = r_check.json().get('rows', [])
for r in rows:
    print(f"  [{r.get('kb_id')}] {r.get('title')}")

print("\nReingestão concluída com sucesso!")
