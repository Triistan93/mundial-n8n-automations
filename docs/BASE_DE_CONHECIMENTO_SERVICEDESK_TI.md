# Base de Conhecimento & Matriz Operacional — Service Desk TI (Sophia AI)
**Mundial Honda — Diretrizes Consolidadas e Validadas pela Gestão de TI**

---

## 1. Visão Geral do Aprendizado

Para que a **Sophia AI** execute a triagem e o autoatendimento com máxima precisão, sem atritos e em alinhamento estrito com os procedimentos reais da Mundial Honda, esta base de conhecimento foi construída sobre três pilares consolidados:
1. **Auditoria Empírica de Chamados Reais** na Categoria 160 (`Central de TI`), mapeando os maiores solicitantes da rede (*Nataelen Balduino, Karina Volsi, Paula Brenda Gallina, Celeste, Camily Silva, Juliana Masson e Gabrielle Romeu*);
2. **Diretrizes Técnicas Oficiais da Gestão de TI** para fluxos de autoatendimento L1, rotinas automatizadas por robôs e guardrails de segurança operacional;
3. **Indexação Vetorial Híbrida (pgvector)** no banco de dados corporativo (`kb_ti_conhecimento`), abastecendo o motor de busca semântica do agente.

---

## 2. Matriz de Arquétipos Operacionais da Mundial Honda

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      MATRIZ DE OPERAÇÃO & ATENDIMENTO (MUNDIAL TI)                              │
├──────────────────────────┬─────────────────────────────┬────────────────────────────────────────┤
│ Arquétipo                │ Volume / Solicitantes       │ Causa Raiz / Demanda Operacional       │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 1. Emissão ATPV-e        │ 146 tickets (Nataelen,      │ Venda final de motos vs Transferência  │
│    (Detran / RENAVE)     │ Camily, Juliana)            │ entre lojas internas da rede.          │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 2. Telefonia Bitrix      │ 89 tickets (Karina,         │ Ramal não toca, aplicativo ausente,    │
│    & Ramal de Atendimento│ Celeste, Loja Vendas)       │ headset mutado ou som do PC zerado.    │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 3. WhatsApp Corporativo  │ 89 tickets (Nataelen,       │ Espelhamento atrasado, queda de sessão │
│    & Plataforma Fale Fácil│ Karina, Celeste, Vendas)   │ API, canal desconectado ou QR Code.    │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 4. Onboarding & Pacote   │ 85 tickets (Karina, Paula   │ Admissão de novo vendedor/consultor    │
│    de Novos Acessos      │ Brenda, Celeste)            │ com necessidade de kit de sistemas.    │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 5. Reset de Senhas &     │ 73 tickets (Universal:      │ Esquecimento de senha ou bloqueio por  │
│    Autoatendimento L1    │ F&I, Peças, Lojas)          │ tentativas incorretas.                 │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 6. MicroWork Cloud, ICMS │ 62 tickets (Gabrielle,      │ Erro de ICMS e OS resolvidos por       │
│    & Faturamento Loja    │ Paula Brenda, Oficina)      │ bot fiscal autônomo da TI.             │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 7. Exclusão de Grupos de │ Dúvidas recorrentes de loja │ Autoatendimento L1 para chat com       │
│    Chat no Bitrix24      │ (Caixas, consultores)       │ guardrail estrito contra exclusão CRM. │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 8. Integração MyHonda ➡️ │ Marketing, Gestores de Loja │ Leads da montadora não entram no       │
│    Bitrix24 (Leads)      │                             │ funil; parada de robô RPA / servidor.  │
├──────────────────────────┼─────────────────────────────┼────────────────────────────────────────┤
│ 9. Chamados com Apenas   │ Supervisores, Vendedores    │ Card aberto apenas com nome de pessoa; │
│    Nome de Pessoa        │ (Abertura rápida de balcão) │ triagem acolhedora investigativa.      │
└──────────────────────────┴─────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Playbooks Oficiais de Resolução e Triagem L1

### Arquétipo 1: Emissão de ATPV-e (RENAVE & Detran)
* **Público Solicitante:** Setor de F&I e Documentistas (Nataelen `#12190`, Camily `#18436` e Juliana `#4736`).
* **Regra de Ouro da Triagem L1 (Diferenciação Crítica):**
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

### Arquétipo 2: Telefonia Bitrix24 & Ramal Não Toca
* **Público Solicitante:** Vendedores, Balcão e Recepção de Loja.
* **Causas Operacionais Recorrentes:**
  * Colaborador desinstalou ou fechou o aplicativo Bitrix24 e está usando pelo navegador web;
  * Botão mudo físico ativado no controle de volume do fio do headset;
  * Volume geral de áudio do computador (Windows) mutado ou zerado;
  * Falta de atualização do aplicativo instalado.
* **Checklist Guiado de Autoatendimento da Sophia AI:**
  1. **Ambiente Obrigatório:** Verificar se o colaborador está utilizando o **Aplicativo Desktop do Bitrix24 instalado no computador** (o uso do App instalado é o padrão oficial obrigatório na Mundial; o navegador não é o ambiente homologado para telefonia estável);
  2. **Checagem de Áudio Físico:** Conferir se o controle do headset não está com a chave ou botão de **MUTE** ativada (luz vermelha no fio);
  3. **Volume do Windows:** Checar se o ícone de alto-falante na barra de tarefas do Windows não está no mudo.
* **REGRA DE OURO & GUARDRAIL DE SEGURANÇA:**
  * A Sophia AI **NUNCA** deve orientar ou sugerir que o colaborador acesse ou altere configurações de telefonia ou configurações de filas dentro do Bitrix24. Essas telas são restritas exclusivamente aos técnicos e administradores de TI em *Contact Center > Telefonia*.

---

### Arquétipo 3: WhatsApp Corporativo & Espelhamento Atrasado (Fale Fácil)
* **Público Solicitante:** Vendas Online, Consórcio (Karina `#3926`) e Documentação (Nataelen `#12190`).
* **O que Caracteriza o "Espelhamento Atrasado":**
  * A mensagem enviada pelo cliente no WhatsApp físico não chega para o atendente na tela do Bitrix24; **OU**
  * A mensagem enviada pelo atendente no Bitrix24 não é entregue no celular do cliente (delay ou trava de API).
* **Escopo do Bot & Coleta Obrigatória:**
  * O colaborador **NÃO** tem acesso à plataforma Fale Fácil. O papel do robô é colher:
    1. **Escopo da Falha (Pergunta Chave):** Perguntar se o problema está ocorrendo em uma **conexão ou número específico** (e qual número/ramal) OU se está afetando **todas as conexões da concessionária**.
    2. **Linha e Ramal:** Número com DDD (ex: 19 9xxxx-xxxx ou fixo da loja).
    3. **Evidência Mandatória (Uma das duas):**
       * **Link de um card/cliente de exemplo no Bitrix24** para acompanhamento dos logs de envio/webhook pela TI; **OU**
       * **Print da tela de erro** exibida no sistema (lido via OCR).
    4. **Checagem Guiada no Smartphone Físico:** Pedir para o colaborador olhar em *Configurações/Ajustes > Aparelhos Conectados* do WhatsApp físico e confirmar se consta como Conectado ou Desconectado.
* **Ação Técnica da TI:** A TI acessa a plataforma Fale Fácil, reinicia as conexões da instância, aciona o suporte da Fale Fácil/Bitrix ou solicita a leitura de um novo QR Code caso a sessão tenha sido revogada.

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

### Arquétipo 5: Reset de Senhas & Autoatendimento L1
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

### Arquétipo 6: MicroWork Cloud — Erros de ICMS e OS (Ajuste por Bot Fiscal)
* **Público Solicitante:** Faturistas (Gabrielle Romeu `#342040`) e Supervisão de Loja (Paula Brenda `#4272`).
* **Resolução Técnica Automatizada:**
  * A equipe de TI não precisa alterar manualmente tabelas de impostos: a Mundial conta com um **robô/bot fiscal dedicado** que já tem a rotina mapeada e executa a liberação e correção de ICMS de forma 100% autônoma.
* **Coleta Mandatória para Alimentar o Robô:**
  1. **Link do Card de Negócio no Bitrix24** (se existir);
  2. **Número da Ordem de Serviço (OS)** ou **Número do Pedido / NF**;
  3. **Chassi Completo da Motocicleta** (17 dígitos iniciados por `9C2...`);
  4. **Print da Tela com o Código de Erro de ICMS** (processado pelo OCR Vision).

---

### Arquétipo 7: Dúvida de Uso do Bitrix24 — Exclusão de Grupos de Chat (L1)
* **Público Solicitante:** Caixas, Consultores e Assistentes de Vendas.
* **Regra Operacional:**
  * Usuários de loja possuem permissão para excluir **grupos de chat/trabalho** desde que eles próprios tenham criado o grupo e figurem como proprietários/administradores dele.
* **Passo a Passo Guiado de Auto-Resolução L1:**
  1. Abrir o grupo de chat no Bitrix24;
  2. No canto superior direito, clicar em **'Sobre o grupo'**;
  3. No menu **'Ações'**, clicar em **'Excluir grupo'**;
  4. Confirmar a exclusão. Se o usuário confirmar a exclusão com sucesso, finalizar como **`RESOLVED_L1`**.
* **GUARDRAIL CRÍTICO DE SEGURANÇA DE DADOS:**
  * A Sophia AI **NUNCA** pode orientar, sugerir ou ensinar usuários a excluir:
    * Cards de negócio (deals) no CRM;
    * Contatos ou empresas da base de clientes;
    * Mensagens do histórico de atendimento do WhatsApp.

---

### Arquétipo 8: Integração MyHonda ➡️ Bitrix24 (Leads da Montadora)
* **Público Solicitante:** Marketing e Gestores de Loja.
* **Causa Técnica:** Parada pontual do script RPA de integração, máquina servidora reiniciada/desligada ou sessão expirada no portal da montadora Honda.
* **Coleta Obrigatória pela Sophia AI:**
  1. **Data e Horário do Último Lead Recebido:** Quando foi o último lead que entrou no Bitrix24?
  2. **Origem da Constatação:** Onde a pessoa identificou a falta (se verificou diretamente no portal MyHonda da montadora, em planilha de acompanhamento ou se foi queixa de cliente)?
* **Ação Técnica:** A TI acessa o servidor de automação, valida a execução do script e normaliza a fila de ingestão de leads.

---

### Arquétipo 9: Chamados Abertos Apenas com Nome de Pessoa
* **Contexto:** Colaboradores abrem tickets rápidos digitando apenas nomes no título (ex: "Lucas Silva", "Paula", "Amanda Vendas") sem preencher comentários.
* **Conduta da Sophia AI (Acolhimento Proativo):**
  1. A Sophia lê o solicitante, a loja e o nome informado no card;
  2. Dispara a pergunta clarificadora estruturada no chat:
     > *"Olá! Notei que seu chamado cita [Nome]. Para que eu possa te ajudar com rapidez: você precisa da criação de novos acessos para este colaborador, redefinição de senha esquecida, alteração de permissão/fila de atendimento ou desligamento/desativação de usuário?"*
  3. Conforme o usuário responde, a Sophia direciona para o playbook específico (Onboarding, Senhas ou Telefonia) e conclui a coleta de dados sem atritos.

---

### Arquétipo 10: Robôs de Automação RPA (Entrada Honda, Entrada Grupo, Vigia e Faturamento)
* **Público Solicitante:** Acessórios, Estoque, Peças, Faturamento e Vendas (Danielly `#439968`, Balcão Peças).
* **Sintomas:** Card do robô travado em processamento, solicitação de entrada em loop, nota fiscal não finalizada pelo robô, robô parado.
* **DIRETIVA ESTRITA DA GESTÃO DE TI:**
  * Trata-se de um serviço autônomo em servidor de backend corporativo. A Sophia AI **NUNCA** deve orientar o usuário a fechar navegador, reiniciar computador ou limpar cookies!
* **Conduta Obrigatória da Sophia AI:**
  1. **Link do Card:** Solicitar o link do card no Bitrix24 onde o robô está travado (ex: `https://b24-88dbfb.bitrix24.com.br/crm/deal/details/XXXXX/`);
  2. **Conferência de Dados:** Perguntar se o colaborador já conferiu se todos os dados do card estão corretos (número da nota, chassi, fornecedor, valores);
  3. **Escalonamento Imediato para a TI (L2):** Imediatamente após a resposta da pessoa (ou se ela já forneceu o link e confirmou os dados), concluir a triagem (`action: COMPLETE`) com alta urgência e direcionar para a TI intervir no robô no servidor.

---

### Arquétipo 11: Liberação de Permissão / Módulo no Bitrix24 (CRM, Tarefas, Folgas e Tickets)
* **Público Solicitante:** Gerentes de Loja (ex: Hadner `#2606`, Celeste `#4880`, Silvana `#2644`) e Supervisores solicitando acesso para membros de equipe (mecânicos, caixas, consultores).
* **Sintomas:** "liberar CRM para mecânico", "não aparece a opção de CRM no Bitrix", "liberar acesso para cards de folga e tickets".
* **DIRETIVA ESTRITA DA GESTÃO DE TI:**
  1. **Separação de Papéis:** O usuário falando no chat é o **gestor responsável** (ex: Hadner). A Sophia deve sempre se dirigir ao gestor pelo nome dele e registrar que o acesso solicitado é para o **colaborador indicado** (ex: Mecânico Ailton).
  2. **Validação Rápida:** Se o usuário confirmar que testou no celular e no computador e o menu não aparece, trata-se de **permissão de perfil/módulo no Bitrix24**.
  3. **Escopo Limpo de Perguntas:** A Sophia **NUNCA** deve fazer perguntas irrelevantes de telefonia, chip de WhatsApp ou compras de hardware para pedidos pontuais de permissão de sistema para colaboradores já contratados.
  4. **Conclusão e Encaminhamento:** Concluir a triagem imediatamente (`action: COMPLETE`) com prioridade B01 P4 (Baixo) e registrar os dados estruturados: Gestor Solicitante, Colaborador Beneficiário, Sistema/Módulo (Bitrix24 CRM / Folgas / Tickets), Loja e resultado dos testes.
