---
id: "KB-015"
titulo: "WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil"
sistemas: ["WhatsApp Corporativo", "Bitrix24 Contact Center", "Plataforma Fale Fácil", "Meta WhatsApp Business"]
palavras_chave: ["whatsapp", "wpp", "fale facil", "contact center", "espelhamento", "canal desconectado", "qr code", "qrcode", "ler qr code", "mensagens não chegam", "não envia mensagem", "número banido", "tudo vermelho", "canal individual", "f&i doc", "linha corporativa", "desconectou do bitrix", "mensagens atrasadas", "template bitrix"]
---

# KB-015 - WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil

## Quando usar
O colaborador relata qualquer um dos seguintes sintomas:
- *"As mensagens do meu WhatsApp não estão espelhando no Bitrix"*
- *"O canal individual desconectou e precisa de QR Code"*
- *"Não consigo enviar mensagens para os clientes pelo Bitrix (aparece ponto de exclamação vermelho)"*
- *"Clientes dizem que mandam mensagens mas não recebo nada no Contact Center"*
- *"Canal Fale Fácil / F&I DOC / Canal da Loja está com erro ou tudo vermelho"*
- *"A IA ou as mensagens pararam de funcionar"*

## Aplica-se a
Consultores de vendas de motocicletas, pós-venda, recepção, peças, gestores e equipes de atendimento que utilizam o Bitrix24 Contact Center integrado à plataforma Fale Fácil em todas as concessionárias da Rede Mundial Honda.

---

## Procedimento Operacional Padrão (Passo a Passo Oficial)

Nas ocorrências envolvendo números e canais corporativos de WhatsApp, o atendimento de suporte de TI segue rigorosamente o seguinte roteiro:

### 1. Identificar qual é a conexão e a linha afetada
- O agente / operador de TI identifica exatamente qual linha está com instabilidade:
  - **Número corporativo com DDD** (ex: `19 9xxxx-xxxx` ou `19 3120-0044`);
  - **Tipo de canal:** Canal individual do consultor (celular físico) ou Canal geral da loja/departamento (Fale Fácil, F&I DOC, Sophia, Recepção);
  - **Nome completo do consultor e loja/filial.**

### 2. Diagnosticar o sintoma real da conexão
- Verificar qual comportamento está ocorrendo:
  - **Problema de envio:** O consultor digita no Bitrix, mas a mensagem fica com ícone de erro/relógio ou falha na entrega.
  - **Problema de recebimento:** O cliente externo responde pelo WhatsApp, mas o chat não abre ou não atualiza no Bitrix Contact Center.
  - **Oscilação total / Desconexão:** O canal exibe aviso de desconectado, barra vermelha ou ausência de sincronização.

### 3. Realizar testes práticos de envio e recebimento
- **Teste de envio:** Enviar uma mensagem de teste pelo Bitrix Contact Center diretamente para o número de teste da equipe ou para o próprio celular do consultor.
- **Teste de recebimento:** Enviar uma mensagem a partir de outro celular para o número corporativo e checar se o card/chat é criado no Bitrix.
- **Checagem de internet do celular:** No caso de canal individual, certificar-se de que o aparelho físico do consultor está ligado, com bateria e conectado a uma rede Wi-Fi estável ou dados móveis 4G/5G.

### 4. Verificar se o número foi banido pela Meta / WhatsApp
- Conferir diretamente na tela do aplicativo WhatsApp instalado no smartphone corporativo da loja/consultor:
  - **Se o número foi BANIDO:** O aplicativo exibe uma mensagem explícita da Meta: *"Esta conta está impedida de usar o WhatsApp"* ou *"Esta conta não tem permissão para usar o WhatsApp"*.
  - **Ação em caso de banimento:** O autoatendimento L1 não pode reverter banimento. O chamado é escalonado com **Urgência Alta (P2)** para a equipe de TI / Gestão de Telefonia para protocolo formal de contestação e suporte com a Meta/operadora ou providência de nova linha SIM.

### 5. Desconectar da plataforma e reconectar lendo o QR Code
- Caso o número **NÃO** esteja banido (o WhatsApp no aparelho abre normalmente):
  - A falha trata-se de desautenticação de sessão na API da plataforma integradora (**Fale Fácil**).
  - A equipe de TI ou o painel administrativo da Fale Fácil realiza a desconexão forçada da instância vinculada à linha.
  - É gerado um novo **QR Code** de autenticação para o canal.
  - O consultor abre o WhatsApp no smartphone corporativo ➔ toca em **Menu / Configurações (três pontinhos ou engrenagem)** ➔ **Aparelhos Conectados** ➔ **Conectar um aparelho** e realiza a leitura do novo QR Code exibido.
  - Aguarda 1 a 2 minutos para sincronização das conversas e refaz o teste de envio e recebimento.

### 6. Escalonar para o Suporte da Fale Fácil (se o problema persistir)
- Caso após a leitura do QR Code a conexão ainda não suba, exiba erro de WebSocket/API ou continue sem transmitir mensagens:
  - Acionar imediatamente o canal oficial de **Suporte da Fale Fácil** informando:
    1. Nome da Instância / ID da Conexão;
    2. Número corporativo completo com DDD;
    3. Horário do início da falha e comportamento observado (print do erro na plataforma e no Bitrix);
    4. Confirmação de que o aparelho físico está ativo e que o QR Code já foi lido sem sucesso.
  - O chamado no Bitrix24 é atualizado com prioridade **P2 (Alta)** com todas as evidências registradas na Timeline.

---

## O que Coletar no Chamado para a TI
Para que o atendimento seja imediato sem idas e vindas de mensagens:
1. **Número corporativo com DDD** afetado;
2. **Nome do Consultor e Filial/Loja**;
3. **Tipo de canal:** Individual ou Geral da Loja;
4. **Comportamento:** Não envia, não recebe ou desconectou;
5. **Status no aparelho físico:** Se o WhatsApp está abrindo normalmente no celular e se o número NÃO está banido;
6. **Print da tela** do erro no Bitrix ou no celular.

## Resultado Esperado
O canal é reautenticado via QR Code na plataforma Fale Fácil, as mensagens voltam a ser transmitidas bidirecionalmente e o colaborador continua seu atendimento comercial sem perder leads.

## Artigos Relacionados
- **KB-011:** Bitrix24 (Cache Ctrl+F5 e Telefonia de Voz)
- **KB-003:** Verificar conexão com a internet e rede da loja
- **KB-010:** Como escalar um chamado para o N2
