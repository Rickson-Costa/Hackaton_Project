# 📖 Manual do Usuário - Sistema FUNETEC

## Sumário
1. [Visão Geral](#visão-geral)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Gestão de Clientes](#gestão-de-clientes)
5. [Gestão de Prestadores](#gestão-de-prestadores)
6. [Gestão de Projetos](#gestão-de-projetos)
7. [Gestão de Contratos](#gestão-de-contratos)
8. [Controle Financeiro](#controle-financeiro)
9. [Relatórios](#relatórios)
10. [Sistema de Alertas](#sistema-de-alertas)

---

## 🔍 Visão Geral

O **Sistema FUNETEC** é uma plataforma completa para gestão de contratos de projetos de prestação de serviços. O sistema controla custos, prazos, pagamentos e oferece diferenciação completa entre prestadores Pessoa Física (PF) e Pessoa Jurídica (PJ).

### ✅ Funcionalidades Principais
- **Cadastro completo** de clientes, prestadores e projetos
- **Controle financeiro** com gestão de parcelas e pagamentos
- **Dashboard analítico** com indicadores visuais
- **Sistema de alertas** para prazos e inadimplência
- **Relatórios personalizados** para diferentes perfis de usuário
- **Diferenciação fiscal** automática entre PF e PJ

---

## 🔐 Acesso ao Sistema

### Login
1. Acesse a URL do sistema
2. Digite seu **usuário** e **senha**
3. Clique em "Entrar"

### Perfis de Usuário
O sistema possui diferentes níveis de acesso:
- **Admin**: Acesso total ao sistema
- **TI**: Gestão técnica e configurações
- **Fiscal**: Controle de contratos e documentação
- **Financeiro**: Gestão de pagamentos e inadimplência
- **Analista**: Consulta e relatórios
- **Cliente**: Acesso limitado aos próprios projetos

---

## 📊 Dashboard Principal

O **Dashboard** é a tela inicial que apresenta uma visão geral do sistema:

### KPIs Principais
- **Projetos Ativos**: Número de projetos em andamento
- **Contratos PF/PJ**: Separação por tipo de pessoa
- **Inadimplência**: Percentual e valor em atraso
- **Crescimento**: Variação mensal de projetos

### Gráficos Disponíveis
1. **Previsto vs Realizado**: Comparação de valores orçados e executados
2. **Status dos Projetos**: Distribuição por situação (Em andamento, Concluído, etc.)
3. **Vencimentos**: Parcelas vencendo nos próximos dias

### Sistema de Semáforos
- 🟢 **Verde**: Situação normal
- 🟡 **Amarelo**: Atenção necessária
- 🔴 **Vermelho**: Situação crítica

---

## 👥 Gestão de Clientes

### Cadastrar Novo Cliente
1. Acesse **"Clientes"** no menu principal
2. Clique em **"Novo Cliente"**
3. Preencha os dados:
   - **Tipo de Pessoa**: PF ou PJ
   - **Nome/Razão Social**
   - **CPF/CNPJ** (conforme o tipo)
   - **E-mail** e **Telefone**
4. Clique em **"Salvar"**

### Consultar Clientes
- **Lista**: Visualize todos os clientes cadastrados
- **Busca**: Use filtros por nome, documento ou tipo
- **Detalhes**: Clique no cliente para ver informações completas

### Editar Cliente
1. Acesse a lista de clientes
2. Clique no cliente desejado
3. Clique em **"Editar"**
4. Modifique os dados necessários
5. Clique em **"Salvar"**

---

## 🔧 Gestão de Prestadores

### Cadastrar Prestador (PF/PJ)

#### Pessoa Física (PF)
1. Acesse **"Contratos"** → **"Prestadores"**
2. Clique em **"Novo Prestador"**
3. Selecione **"Pessoa Física"**
4. Preencha:
   - **Nome completo**
   - **CPF** e **RG**
   - **Dados de contato**
   - **Endereço completo**
   - **Dados bancários**

#### Pessoa Jurídica (PJ)
1. Siga os mesmos passos iniciais
2. Selecione **"Pessoa Jurídica"**
3. Preencha:
   - **Razão Social** e **Nome Fantasia**
   - **CNPJ**, **Inscrição Estadual/Municipal**
   - **Dados de contato**
   - **Endereço da empresa**
   - **Dados bancários**

### Regras Fiscais Automáticas
- **PF**: Sistema calcula INSS, IRRF e ISS automaticamente
- **PJ**: Aplica retenções de ISS, IRRF, PIS/COFINS/CSLL
- **Validações**: CPF/CNPJ são validados automaticamente

---

## 📋 Gestão de Projetos

### Criar Novo Projeto
1. Acesse **"Projetos"**
2. Clique em **"Novo Projeto"**
3. Preencha:
   - **Código do Projeto** (único)
   - **Nome descritivo**
   - **Data de Início** e **Encerramento**
   - **Valor orçado**
   - **Situação inicial**

### Situações do Projeto
- **Aguardando Início**: Projeto aprovado, aguardando início
- **Em Andamento**: Projeto sendo executado
- **Paralisado**: Temporariamente parado
- **Suspenso**: Suspenso por decisão
- **Cancelado**: Cancelado definitivamente
- **Concluído**: Finalizado com sucesso

### Controle de Custos
- **Custo Previsto**: Valor original do orçamento
- **Custo Realizado**: Valor efetivamente gasto
- **Indicador Visual**: Semáforo que indica a situação
  - 🟢 Dentro do orçamento
  - 🟡 Próximo do limite (90-100%)
  - 🔴 Orçamento estourado (>100%)

---

## 📄 Gestão de Contratos

### Criar Contrato
1. Acesse **"Contratos"**
2. Clique em **"Novo Contrato"**
3. Preencha:
   - **Número** (gerado automaticamente)
   - **Código da Ordem** de origem
   - **Descrição** dos serviços
   - **Prestador** (CPF/CNPJ)
   - **Datas de início e fim**
   - **Valor total**

### Modalidades de Pagamento

#### Pagamento Único
- **Uma parcela** com valor total
- **Data de vencimento** definida
- **Sem divisões**

#### Pagamento em Duas Parcelas
- **50% na assinatura** (ou personalizado)
- **50% na entrega** (ou personalizado)
- **Datas específicas** para cada parcela

### Status do Contrato
- **Lançado**: Criado, aguardando assinatura
- **Assinado**: Assinado, pronto para execução
- **Em Andamento**: Sendo executado
- **Suspenso**: Temporariamente parado
- **Cancelado**: Cancelado
- **Finalizado**: Concluído

---

## 💰 Controle Financeiro

### Gestão de Parcelas
Cada contrato gera **parcelas automáticas** conforme a modalidade:

#### Visualizar Parcelas
1. Acesse o **detalhes do contrato**
2. Veja a lista de **parcelas** na parte inferior
3. Cada parcela mostra:
   - **Número da parcela**
   - **Valor** e **data de vencimento**
   - **Status** (Pendente, Paga, Vencida)
   - **Valor já pago**

#### Registrar Pagamento
1. Na lista de parcelas, clique em **"Registrar Pagamento"**
2. Informe o **valor pago**
3. O sistema atualiza automaticamente:
   - **Status da parcela**
   - **Valor pendente**
   - **Data do pagamento**

#### Status das Parcelas
- **Pendente**: Aguardando pagamento
- **Parcialmente Paga**: Pagamento parcial registrado
- **Paga**: Valor total quitado
- **Vencida**: Passou da data sem pagamento

### Controle de Inadimplência
- **Dashboard** mostra percentual de inadimplência
- **Alertas automáticos** para parcelas vencidas
- **Relatórios** de valores em atraso

---

## 📈 Relatórios

### Tipos de Relatórios

#### Relatórios Financeiros
- **Fluxo de Caixa**: Entradas e saídas por período
- **Inadimplência**: Valores em atraso por cliente/contrato
- **Impostos Retidos**: Separação PF/PJ
- **Resumo Mensal**: Totais por mês

#### Relatórios de Projetos
- **Status Geral**: Situação de todos os projetos
- **Orçamento vs Realizado**: Comparativo de custos
- **Prazo vs Execução**: Análise de cronogramas
- **Projetos por Cliente**: Agrupamento por contratante

#### Relatórios de Contratos
- **Contratos por Prestador**: PF e PJ separadamente
- **Vencimentos**: Próximos vencimentos
- **Histórico de Pagamentos**: Registros de recebimentos

### Gerar Relatório
1. Acesse **"Relatórios"**
2. Selecione o **tipo desejado**
3. Defina o **período** (se aplicável)
4. Escolha **filtros** específicos
5. Clique em **"Gerar"**
6. **Exporte** em PDF ou Excel

---

## 🚨 Sistema de Alertas

### Tipos de Alertas

#### Alertas de Prazo
- **Projetos críticos**: Vencimento em 7 dias ou menos
- **Projetos atrasados**: Passaram da data limite
- **Cor do alerta**:
  - 🟡 Amarelo: Próximo do vencimento (≤7 dias)
  - 🔴 Vermelho: Atrasado ou crítico (≤2 dias)

#### Alertas Financeiros
- **Parcelas vencidas**: Pagamentos em atraso
- **Orçamentos estourados**: Custos acima do previsto
- **Inadimplência alta**: Percentual acima do aceitável

#### Alertas de Aceite
- **Entregas pendentes**: Aguardando aceite do cliente
- **Aceites vencidos**: Passaram do prazo de aceite

### Visualização de Alertas
- **Dashboard principal**: Seção específica de alertas
- **Indicadores visuais**: Cores e ícones de atenção
- **Detalhamento**: Clique no alerta para mais informações

---

## 🔧 Funções Avançadas

### Aceite de Entregas
1. Acesse o **contrato** específico
2. Clique em **"Registrar Aceite"**
3. Confirme o **aceite da entrega**
4. Sistema registra **data e usuário**
5. **Libera** próximas parcelas (se configurado)

### Regras de Cálculo
#### Pessoa Física (PF)
- **INSS**: 11% sobre o valor (limite do teto)
- **IRRF**: Conforme tabela progressiva
- **ISS**: Percentual municipal (geralmente 2-5%)

#### Pessoa Jurídica (PJ)
- **ISS**: Conforme município
- **IRRF**: 1,5% sobre serviços
- **PIS/COFINS/CSLL**: Conforme regime tributário

### Backup e Segurança
- **Auditoria**: Todas as ações são registradas
- **Controle de acesso**: Por perfil de usuário
- **Logs de sistema**: Rastreamento completo

---

## 📞 Suporte

### Problemas Comuns

#### "Não consigo criar contrato"
- Verifique se o **prestador está cadastrado**
- Confirme se há **ordem de serviço** vinculada
- Verifique **permissões** do seu usuário

#### "Pagamento não está sendo registrado"
- Confirme o **valor informado**
- Verifique se a **parcela existe**
- Valor não pode ser **maior que o pendente**

#### "Relatório não carrega"
- Reduza o **período** consultado
- Verifique sua **conexão**
- Tente **filtros mais específicos**

### Contato de Suporte
- **Email**: suporte@funetec.org.br
- **Telefone**: (83) 3000-0000
- **Horário**: Segunda a sexta, 8h às 17h

---

## 📋 Glossário

- **PF**: Pessoa Física
- **PJ**: Pessoa Jurídica
- **INSS**: Instituto Nacional do Seguro Social
- **IRRF**: Imposto de Renda Retido na Fonte
- **ISS**: Imposto Sobre Serviços
- **KPI**: Key Performance Indicator (Indicador-chave de Performance)
- **Semáforo**: Sistema visual de cores para status
- **Dashboard**: Painel principal com resumos e gráficos

---

*Documento gerado em: Setembro 2025*  
*Versão do Sistema: 1.0*  
*FUNETEC-PB - Fundação de Educação, Tecnologia e Cultura da Paraíba*