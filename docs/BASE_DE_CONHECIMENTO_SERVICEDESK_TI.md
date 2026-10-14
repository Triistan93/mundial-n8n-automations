# Base de Conhecimento & Matriz Operacional — Service Desk TI (Sophia AI)
**Mundial Honda — Diretrizes Validadas pela Gestão de TI**

---

## 1. Visão Geral do Aprendizado

Para que a **Sophia AI** resolva chamados com máxima precisão, sem atritos e em alinhamento estrito com os procedimentos reais da Mundial Honda, a base de conhecimento foi construída sobre duas fontes consolidadas:
1. **Auditoria Empírica de 596 Chamados Reais** abertos pelo grupo dos maiores solicitantes da empresa (*Nataelen Balduino, Karina Volsi, Paula Brenda Gallina, Celeste, Camily Silva, Juliana Masson e Gabrielle Romeu*);
2. **Diretrizes Técnicas Oficiais da Gestão de TI** para os 4 temas centrais de suporte.

---

## 2. Matriz dos 5 Grandes Arquétipos Operacionais

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      MATRIZ DE OPERAÇÃO & ATENDIMENTO (MUNDIAL TI)                              │
├──────────────────────────┬─────────────────────────────┬────────────────────────────────────────┤
│ Arquétipo                │ Volume / Solicitantes       │ Causa Raiz / Demanda Operacional       │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 1. Emissão ATPV-e        │ 146 tickets (Nataelen,      │ Venda final de motos vs Transferência  │
│    (Detran / RENAVE)     │ Camily, Juliana)            │ entre lojas internas da rede.          │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 2. WhatsApp & Contact    │ 89 tickets (Nataelen,       │ Queda de sessão, desconexão de canal   │
│    Center / Telefonia    │ Karina, Celeste, Vendas)    │ Fale Fácil ou falha de espelhamento.   │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 3. Onboarding & Pacote   │ 85 tickets (Karina, Paula   │ Admissão de novo vendedor/consultor    │
│    de Novos Acessos      │ Brenda, Celeste)            │ com necessidade de kit de sistemas.    │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 4. Reset de Senhas &     │ 73 tickets (Universal:      │ Esquecimento de senha ou bloqueio por  │
│    Autoatendimento L1    │ F&I, Peças, Lojas)          │ tentativas incorretas.                 │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 5. MicroWork, OS & NF    │ 62 tickets (Gabrielle,      │ Erro de ICMS, tipo de movimento        │
│    (Faturamento de Loja) │ Paula Brenda, Araras)       │ ou emissão de nota de demonstração.    │
└──────────────────────────┴─────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Playbooks Oficiais de Resolução e Triagem L1

### Arquétipo 1: Emissão de ATPV-e (RENAVE & Detran)
* **Público Solicitante:** Setor de F&I e Documentistas (Nataelen `#12190`, Camily `#18436` e Juliana `#4736`).
* **Regra de Ouro da Triagem L1:**
  1. **Transferência entre Lojas Internas:** A equipe de TI **NÃO** emite ATPV para transferências internas entre concessionárias da rede Mundial. Se for transferência, a Sophia AI orienta imediatamente o colaborador a seguir o fluxo padrão de movimentação de estoque de veículos.
  2. **Venda para Cliente Final:** Exige a emissão da ATPV-e / Intenção de Venda pela TI.
* **Coleta Obrigatória pela Sophia AI:**
  * **Chassi Completo:** Exatamente 17 caracteres alfanuméricos, iniciando obrigatoriamente por **`9C2...`**.
  * **Print do Erro em Tela:** Captura da tela do MicroWork com a mensagem/código de erro (analisada via OCR Vision GPT-4o).
* **Procedimento Técnico da Equipe de TI no MicroWork Cloud:**
  * **Rotina Oficial:** [Renave - MicroWork CLOUD DMS](https://microworkcloud.com.br/cloud/#/veiculo/estoque/renave)
  * **Passo a Passo:**
    1. Filtrar pelo Chassi informado;
    2. Em Período, selecionar a opção **`PERÍODO`**;
    3. Desmarcar o filtro **`NOVO`**;
    4. Selecionar a **Filial** correspondente;
    5. Clicar em **Busca** e transmitir a intenção de venda.

---

### Arquétipo 2: Reset de Senhas & Autoatendimento L1
* **Público Solicitante:** Universal (F&I, Vendas, Peças e Oficina).
* **Fluxo de Autoatendimento L1 (Resolução Direta pelo Usuário):**
  * **Sistemas com Self-Service:** **Bitrix24**, **MicroWork Cloud** e **Plataforma FANDI** possuem o botão nativo *"Esqueci minha senha"* na tela de login, que dispara o e-mail de redefinição direto para a caixa de entrada institucional do colaborador.
  * **Comportamento da Sophia AI:**
    > *"Antes de abrirmos um chamado para a equipe técnica, você pode usar a opção **'Esqueci minha senha'** na tela de login do [Bitrix/Cloud/Fandi]. O sistema enviará o link de redefinição diretamente para o seu e-mail corporativo. Você já tentou este procedimento?"*
  * Se o colaborador redefinir com sucesso, o chamado é finalizado como **`RESOLVED_L1`** (sem fila e sem acionar técnicos).
  * Se o colaborador não tiver acesso ao e-mail ou a conta estiver bloqueada por excesso de tentativas, transborda para a TI.
* **Sistemas com Intervenção Manual da TI (L2):**
  * **IHS Motocicleta (Honda)**, **Windows / Rede Corporativa** e **VPN** dependem de redefinição manual pelo suporte técnico no console de administração.

---

### Arquétipo 3: WhatsApp Corporativo, Contact Center & Fale Fácil
* **Público Solicitante:** Vendas Online, Consórcio (Karina `#3926`) e Documentação (Nataelen `#12190`).
* **Sintomas:** Canal individual desconectado, mensagens não espelham no Bitrix, QR Code expirado ou número do F&I não envia mensagem.
* **Escopo do Bot & Coleta Obrigatória:**
  * O colaborador **NÃO** tem acesso à plataforma Fale Fácil. O papel do robô é colher:
    1. **Número Corporativo / Ramal Afetado** (com DDD);
    2. **Evidência Técnica Obrigatória:**
       * **Print da tela de erro** (analisado pelo OCR Vision); **OU**
       * Se a mensagem não chega para o cliente, o **link de um card/cliente de exemplo** no Bitrix24 para que a TI acompanhe os logs de envio e resposta.
    3. **Checagem Guiada no Smartphone Físico:** Pedir para o colaborador olhar em *Configurações > Dispositivos Conectados* do WhatsApp e informar se consta como 'Conectado' ou 'Desconectado'.
* **Ação da Equipe Técnica:** A TI acessa a plataforma Fale Fácil, reinicia a instância da linha, gera novo QR Code se necessário e valida a conexão.

---

### Arquétipo 4: Onboarding & Pacote de Acessos para Novos Colaboradores
* **Público Solicitante:** Gerentes de Loja (Celeste, Silvana, Anderson, Andréia) e Supervisoras (Paula Brenda, Karina Volsi).
* **Checklist Mandatório que a Sophia AI deve Extrair do Gestor:**
  1. **Função / Cargo Exato:** Qual a função do novo colaborador (ex: Consultor de Vendas Novas, Seminovas, Caixa, Faturista, Consultor Técnico)?
  2. **Telefonia Corporativa:** É necessário ativar telefonia (Fale Fácil/ramal)? Se sim, em **qual fila de atendimento** ele deve ser alocado?
  3. **Canal de WhatsApp:** O colaborador utilizará o WhatsApp oficial coletivo da loja ou terá canal individual?
  4. **Equipamentos (Hardware):** A loja/setor já possui computador, monitor e headset disponíveis para uso, ou já foi solicitada a compra de equipamento?
* **Resultado:** O ticket é registrado na Categoria 160 com todas as 4 informações preenchidas, permitindo que a TI crie os acessos em lote sem nenhuma troca de mensagens pendente.

---

### Arquétipo 5: MicroWork Cloud, Faturamento & Notas de Demonstração
* **Público Solicitante:** Faturistas (Gabrielle Romeu `#342040`) e Supervisão ADM (Paula Brenda `#4272`).
* **Sintomas:** Rejeição de ICMS, tipo de movimento bloqueado no Cloud, emissão de nota fiscal de demonstração ou modelo novo de motocicleta com cadastro incorreto.
* **Coleta da Sophia AI:**
  * Número do Pedido Cloud ou Ordem de Serviço (OS);
  * Print da mensagem de rejeição fiscal da SEFAZ ou do erro de permissão no DMS;
  * Chassi envolvido na nota fiscal.
