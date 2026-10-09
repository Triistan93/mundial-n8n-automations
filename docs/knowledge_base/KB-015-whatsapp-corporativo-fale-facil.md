---
id: "KB-015"
titulo: "WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil"
sistemas: ["WhatsApp Corporativo", "Bitrix24 Contact Center", "Plataforma Fale Fácil", "Meta WhatsApp Business"]
palavras_chave: ["whatsapp", "wpp", "fale facil", "contact center", "espelhamento", "canal desconectado", "qr code", "qrcode", "dispositivos conectados", "aparelhos conectados", "mensagens não chegam", "não envia mensagem", "número banido", "tudo vermelho", "canal individual", "f&i doc", "linha corporativa", "desconectou do bitrix"]
---

# KB-015 - WhatsApp Corporativo, Contact Center Bitrix24 e Plataforma Fale Fácil

## Quando usar
O colaborador relata qualquer um dos seguintes sintomas:
- *"As mensagens do meu WhatsApp profissional não estão espelhando no Bitrix"*
- *"O canal individual desconectou do Bitrix / precisa de QR Code"*
- *"Não consigo enviar mensagens para os clientes pelo Bitrix (erro ao enviar / ponto de exclamação vermelho)"*
- *"Clientes dizem que enviaram mensagens mas não chegam no Contact Center"*
- *"Canal Fale Fácil / F&I DOC / Canal da Loja está com oscilação ou tudo vermelho"*
- *"A IA ou o recebimento de mensagens parou"*

## Aplica-se a
Consultores de vendas de motocicletas novas/usadas, pós-venda, recepção, peças, F&I e gestores que utilizam canais de WhatsApp integrados ao Bitrix24 Contact Center através da plataforma parceira **Fale Fácil**.

---

## Divisão de Papéis e Diretriz de Atendimento

> [!IMPORTANT]
> **ATENÇÃO AO ESCOPO DO BOT / AUTOATENDIMENTO:**  
> O colaborador da concessionária **NÃO tem acesso administrativo à plataforma Fale Fácil** e não deve ser instruído a mexer em configurações de servidor, desconectar instâncias de sistema ou tentar gerar QR Code por conta própria.  
> **O papel do Bot de IA é exclusivamente COLHER e CONFIRMAR as informações essenciais** no chat, orientando apenas a checagem que o usuário consegue fazer no próprio celular, para entregar o chamado 100% diagnosticado para a equipe técnica de TI atuar no painel.

---

## 1. Roteiro de Coleta e Confirmação pelo Bot de IA (L1)

Ao receber um chamado sobre WhatsApp Corporativo ou canal do Bitrix, o bot realiza uma triagem acolhedora coletando os seguintes pontos:

1. **Identificação da Conexão e Linha:**
   - Solicita o **número corporativo com DDD** afetado (ex: `19 9xxxx-xxxx` ou `19 3120-0044`);
   - Confirma a loja/unidade e o nome do consultor responsável.

2. **Diagnóstico do Comportamento:**
   - Pergunta se o problema é **para enviar mensagens**, **para receber mensagens** ou se **parou tudo (ambos)**.

3. **Checagem Guiada no Smartphone Corporativo:**
   - O bot orienta o colaborador a fazer uma verificação visual simples no próprio aparelho físico:
     * *Passo no celular:* Abrir o WhatsApp ➔ tocar em **Configurações** (ou Ajustes / três pontinhos) ➔ **Dispositivos conectados** (ou Aparelhos conectados);
     * *Pergunta ao colaborador:* `"Você consegue dar uma olhadinha no seu WhatsApp em Configurações > Dispositivos conectados e me dizer se a conexão aparece como conectada ou se aparece desconectada?"`
     * *Verificação de banimento:* O colaborador confirma se o WhatsApp está abrindo normalmente no aparelho (sem aviso de conta banida/suspensa pela Meta).

4. **Conclusão Imediata da Triagem (`action: COMPLETE`):**
   - Com o número com DDD, o sintoma (envio/recebimento) e o status visto em *Dispositivos conectados*, o bot **NÃO tenta inventar procedimentos complexos**:
   - Conclui a triagem com mensagem amigável e registra todas as evidências na timeline para que a TI execute as ações na plataforma.

---

## 2. Roteiro de Resolução Técnica pela Equipe de TI (N2 / Fale Fácil)

Com os dados coletados pelo bot, o técnico de TI executa o fluxo oficial no painel:

1. **Acessar a Plataforma Fale Fácil:**
   - Localiza a conexão correspondente ao número corporativo informado pelo colaborador.
2. **Avaliar o Status da Conexão:**
   - Se o colaborador relatou desconectado ou se a instância estiver com status vermelho/falha:
   - Realizar a **desconexão da sessão** na plataforma Fale Fácil;
   - Gerar um novo **QR Code** de autenticação;
   - Disponibilizar o QR Code para o colaborador realizar a leitura no aparelho (*Configurações > Dispositivos conectados > Conectar um aparelho*).
3. **Se o Número Estiver Banido pela Meta:**
   - Se o colaborador relatou a mensagem *"Esta conta está impedida de usar o WhatsApp"*, a TI aciona o protocolo de contestação junto ao suporte da Meta/operadora ou providencia a troca do chip SIM.
4. **Acionamento do Suporte da Fale Fácil:**
   - Caso após a leitura do QR Code a conexão ainda não suba ou persista sem tráfego de mensagens, a TI abre chamado com o suporte oficial da Fale Fácil informando o ID da instância, número com DDD e prints do erro.

---

## Dados Estruturados Registrados no Chamado
- **Número Corporativo:** (com DDD)
- **Consultor / Filial:**
- **Tipo de Falha:** Envio, Recebimento ou Queda Total
- **Status em Dispositivos Conectados:** Conectado / Desconectado
- **Status do WhatsApp no Celular:** Normal / Suspeita de Banimento

## Artigos Relacionados
- **KB-011:** Bitrix24 (Cache Ctrl+F5 e Telefonia)
- **KB-010:** Como escalar um chamado para o N2
