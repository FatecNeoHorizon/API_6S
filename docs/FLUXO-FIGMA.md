# Fluxo do Usuário — Zeus

[Voltar ao README principal](../README.md#date-sprint-backlog)

---

## 🎯 Objetivo deste Documento

Este documento descreve o fluxo completo da aplicação **Zeus** — Plataforma de Análise de Dados ANEEL — detalhando cada tela, seus componentes, ações disponíveis e regras de negócio associadas.

---

## 🗺️ Visão Geral do Fluxo

```
Login
  ├── Primeiro Acesso (novo usuário)
  │     ├── Passo 1 — Definir Senha
  │     └── Passo 2 — Aceitar Termos
  └── Usuário já cadastrado
        └── Dashboard
              ├── Mapa de Calor
              ├── Indicadores DEC/FEC
              │     ├── Aba DEC/FEC
              │     └── Aba Perdas
              ├── Estrutura das Redes
              ├── Gestão de Usuários
              │     ├── Cadastrar Usuário
              │     ├── Editar Usuário
              │     └── Excluir Usuário
              ├── Gestão de Termos
              │     ├── Cadastrar Termo
              │     ├── Editar Termo
              │     └── Excluir Rascunho
              └── Meu Perfil
```

---

## 1. Login

**Rota:** `/login`  
**Acesso:** Público

### Descrição

Tela inicial da plataforma. O usuário insere suas credenciais para acessar o sistema.

![Login](/image/figma/login.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Logo + Nome | Ícone Zeus centralizado com subtítulo "Plataforma de Análise de Dados ANEEL" |
| Campo Email | Input de texto com placeholder `seu@email.com` |
| Campo Senha | Input de senha com toggle de visibilidade (ícone olho) |
| Checkbox "Lembrar de mim" | Mantém a sessão ativa entre acessos |
| Link "Esqueceu a senha?" | Redireciona para o fluxo de recuperação de senha |
| Botão "Entrar" | Submete as credenciais para autenticação |
| Rodapé | "Tecsys do Brasil - Todos os direitos reservados" |

### Ações do Usuário

- Preencher email e senha e clicar em **Entrar**
- Marcar "Lembrar de mim" para sessão persistente
- Clicar em "Esqueceu a senha?" para recuperar acesso

### Regras de Negócio

- Credenciais validadas via PostgreSQL (dados sensíveis/LGPD)
- Se for o **primeiro acesso** do usuário, redireciona para o fluxo de Primeiro Acesso
- Se as credenciais forem válidas e o usuário já tiver completado o cadastro, redireciona para o **Dashboard**

---

## 2. Primeiro Acesso

**Rota:** `/primeiro-acesso`  
**Acesso:** Usuários com cadastro pendente (criados pelo administrador)

Fluxo em **2 passos** obrigatórios antes de acessar o sistema.

---

### 2.1 Passo 1 — Definir Senha

### Descrição

O usuário define sua senha de acesso. O sistema exibe os requisitos em tempo real conforme a senha é digitada.

![Primeiro Acesso - Passo 1](/image/figma/primeiro-acesso-1.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Stepper (1 → 2) | Indicador de progresso com passo 1 ativo |
| Campo "Nova Senha" | Input de senha com toggle de visibilidade |
| Checklist de Requisitos | Valida em tempo real: mínimo 8 caracteres, letra minúscula, letra maiúscula, número, caractere especial |
| Campo "Confirmar Senha" | Confirmação da nova senha com toggle de visibilidade |
| Botão "Continuar" | Avança para o Passo 2 (habilitado apenas quando todos os requisitos são atendidos) |

### Regras de Negócio

- O botão "Continuar" permanece desabilitado até que todos os 5 requisitos de senha sejam atendidos e as senhas coincidam
- A senha é armazenada de forma criptografada no PostgreSQL

---

### 2.2 Passo 2 — Aceitar Termos

### Descrição

O usuário lê e aceita os termos obrigatórios antes de concluir o cadastro.

![Primeiro Acesso - Passo 2](/image/figma/primeiro-acesso-2.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Stepper (✓ → 2) | Passo 1 marcado como concluído, passo 2 ativo |
| Accordion "Termos de Uso" | Expansível para leitura completa do documento |
| Checkbox "Li e aceito os Termos de Uso" | Confirmação obrigatória |
| Accordion "Política de Privacidade (LGPD)" | Expansível para leitura completa do documento |
| Checkbox "Li e aceito a Política de Privacidade" | Confirmação obrigatória |
| Botão "Voltar" | Retorna ao Passo 1 |
| Botão "Concluir Cadastro" | Finaliza o onboarding e redireciona ao Dashboard (habilitado apenas com ambos os checkboxes marcados) |

### Regras de Negócio

- Os termos exibidos são os da versão **ativa** mais recente cadastrada na Gestão de Termos
- O aceite é registrado com data/hora e vinculado ao usuário (auditoria LGPD)
- O botão "Concluir Cadastro" só é habilitado quando **ambos** os documentos forem aceitos
- Após conclusão, o usuário é redirecionado para o **Dashboard**

---

## 3. Dashboard

**Rota:** `/dashboard`  
**Acesso:** Todos os perfis autenticados

### Descrição

Visão geral consolidada dos principais indicadores do sistema. Primeiro destino após o login.

![Dashboard](/image/figma/dashboard-1.png)
![Dashboard](/image/figma/dashboard-2.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Card "Total de Distribuidoras" | Número total de distribuidoras ativas com variação vs. período anterior |
| Card "Índice DEC Médio" | DEC médio nacional em horas com variação percentual |
| Card "Índice FEC Médio" | FEC médio nacional em interrupções/consumidor com variação percentual |
| Card "Áreas Críticas" | Número de regiões em estado crítico com variação vs. período anterior |
| Painel "Atividades Recentes" | Lista das últimas ocorrências registradas por região com status (Crítico / Alerta / Normal) |
| Painel "Top Regiões" | Ranking das regiões com maior número de distribuidoras exibindo DEC e FEC por região |
| Menu lateral | Navegação global: Dashboard, Mapa de Calor, Indicadores DEC/FEC, Estrutura das Redes, Gestão de Usuários, Gestão de Termos |
| Avatar + nome do usuário | Canto superior direito com menu de perfil |

### Ações do Usuário

- Visualizar indicadores gerais
- Navegar para qualquer módulo pelo menu lateral
- Acessar "Meu Perfil" pelo avatar no canto superior direito

---

## 4. Mapa de Calor

**Rota:** `/mapa-de-calor`  
**Acesso:** Todos os perfis autenticados

### Descrição

Visualização geográfica dos indicadores de qualidade por estado brasileiro, com mapa interativo colorido por nível de criticidade.

![Mapa de Calor](/image/figma/mapa-de-calor.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Abas de indicador | Filtros de visualização: **DEC**, **FEC**, **Perdas**, **Criticidade** |
| Mapa do Brasil | Mapa interativo com estados coloridos por nível: 🔴 Alta, 🟠 Média, 🟢 Baixa |
| Legenda de criticidade | Exibida sobre o mapa |
| Tooltip ao hover | Exibe estado, região, DEC, FEC e nível de criticidade ao passar o mouse |
| Painel lateral — Estado selecionado | Exibe detalhes do estado clicado: Região, Criticidade, DEC, FEC e botão "Ver Detalhes" |
| Lista "Todos os Estados" | Painel lateral com rolagem listando todos os estados com seus valores de DEC |
| Botão "Filtros Avançados" | Abre filtros adicionais |
| Botão "Exportar" | Exporta a visualização atual |
| Controles de zoom | Botões `+` e `–` no mapa |

### Ações do Usuário

- Alternar entre abas DEC / FEC / Perdas / Criticidade
- Clicar em um estado para ver seus detalhes no painel lateral
- Passar o mouse sobre um estado para ver tooltip rápido
- Clicar em "Ver Detalhes" para aprofundar a análise
- Usar filtros avançados para segmentar a visualização
- Exportar os dados exibidos

---

## 5. Indicadores DEC/FEC

**Rota:** `/indicadores`  
**Acesso:** Todos os perfis autenticados

Página com **2 abas**: DEC/FEC e Perdas.

---

### 5.1 Aba DEC/FEC

### Descrição

Análise detalhada dos indicadores de continuidade de energia elétrica com histórico e ranking de distribuidoras.

![Indicadores DEC/FEC](/image/figma/indicadores-1.png)
![Indicadores DEC/FEC - Ranking](/image/figma/indicadores-2.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Seletor de período | Filtros rápidos: 7 dias, 30 dias, 90 dias, 1 ano, Personalizado |
| Card "DEC Médio Nacional" | Valor atual em horas com variação vs. período anterior |
| Card "FEC Médio Nacional" | Valor atual com variação vs. período anterior |
| Card "Distribuidoras Conformes" | Quantidade dentro da meta (ex: 38/53) com variação |
| Card "Alertas Ativos" | Número de alertas em vermelho com variação |
| Gráfico "Evolução DEC/FEC" | Linha dupla (DEC em azul, FEC em verde) com histórico dos últimos 6 meses |
| Gráfico "Distribuição por Status" | Donut chart com total de distribuidoras e legenda: Conforme (azul), Alerta (laranja), Crítico (vermelho) |
| Tabela "Ranking de Distribuidoras" | Colunas: Distribuidora, DEC, Meta DEC, FEC, Meta FEC, Status — ordenável e filtrável |
| Botão "Filtrar" | Filtros sobre a tabela de ranking |
| Botão "Exportar" | Exporta os dados exibidos |

### Ações do Usuário

- Selecionar período de análise
- Analisar evolução temporal pelo gráfico de linhas
- Filtrar e ordenar o ranking de distribuidoras
- Exportar dados

---

### 5.2 Aba Perdas

### Descrição

Análise das perdas técnicas e não-técnicas das distribuidoras com comparação às metas regulatórias.

![Indicadores - Perdas](/image/figma/indicadores-perdas.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Seletor de período | Mesmo comportamento da aba DEC/FEC |
| Card "Perdas Técnicas" | Percentual atual com meta e barra de progresso (azul = abaixo da meta ✅) |
| Card "Perdas Não-Técnicas" | Percentual atual com meta e barra de progresso (vermelho = acima da meta ⚠️) |
| Card "Perdas Totais" | Soma percentual com meta e indicação de status |
| Gráfico "Evolução das Perdas" | Linha dupla (Perdas Técnicas em azul, Não-Técnicas em vermelho) com histórico mensal |
| Botão "Exportar" | Exporta os dados exibidos |

### Regras de Negócio

- Perdas calculadas a partir dos layers `CTMT`, `UNTRAT` e `UNTRMT` da BDGD
- Cores das barras de progresso indicam conformidade: azul = abaixo da meta, vermelho = acima da meta

---

## 6. Estrutura das Redes

**Rota:** `/estrutura-redes`  
**Acesso:** Todos os perfis autenticados

### Descrição

Visualização da infraestrutura física da rede elétrica por região, com lista de ativos e painel de detalhes ao selecionar um item.

![Estrutura das Redes](/image/figma/redes-1.png)
![Estrutura das Redes - Detalhes](/image/figma/redes-2.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Card "Subestações" | Total de subestações cadastradas |
| Card "Transformadores" | Total de transformadores cadastrados |
| Card "Operacionais" | Total de ativos com status operacional |
| Card "Em Alerta" | Total de ativos em estado de alerta |
| Barra de busca | Busca por nome ou código do ativo |
| Filtro "Todas Regiões" | Dropdown para filtrar por região geográfica |
| Filtro "Todos Tipos" | Dropdown para filtrar por tipo de ativo (Subestação, Transformador) |
| Filtro "Todos Status" | Dropdown para filtrar por status (Operacional, Manutenção, Alerta) |
| Tabela "Ativos da Rede" | Colunas: Ativo, Região, Tensão, Status (badge colorido), Carga (barra de progresso + %) |
| Painel lateral de detalhes | Abre ao clicar em um ativo: Status, Localização, Tensão, MVA, Carga Atual, Temperatura, Transformadores, Alimentadores, Manutenção (última e próxima) |
| Botão "Ver Histórico" | Acessa histórico de manutenção do ativo |
| Botão "Ver no Mapa" | Abre localização do ativo no Mapa de Calor |
| Botão "Atualizar" | Recarrega os dados da listagem |
| Botão "Exportar" | Exporta a listagem de ativos |

### Ações do Usuário

- Buscar ativo por nome ou código
- Filtrar por região, tipo e status
- Clicar em um ativo para abrir o painel de detalhes
- Fechar o painel com o botão `×`
- Ver histórico ou localização no mapa a partir do painel de detalhes

### Regras de Negócio

- Dados originados dos layers `SUB`, `UNTRAT`, `UNTRMT` e `SSDAT` da BDGD
- Status exibido com badges: 🔵 Operacional, 🟡 Em Manutenção, 🔴 Alerta
- Carga exibida como barra de progresso colorida (verde → amarelo → vermelho conforme valor)

---

## 7. Gestão de Usuários

**Rota:** `/gestao-usuarios`  
**Acesso:** Perfil **Administrador** (restrito)

### Descrição

Gerenciamento completo de usuários do sistema com conformidade LGPD.

---

### 7.1 Listagem de Usuários

### Componentes

![Gestão de Usuários](/image/figma/usuario.png)

| Elemento | Descrição |
|:---------|:----------|
| Card "Total de Usuários" | Contagem total de usuários cadastrados |
| Card "Usuários Ativos" | Contagem de usuários com status Ativo |
| Card "Usuários Inativos" | Contagem de usuários com status Inativo |
| Barra de busca | Busca por nome ou email |
| Tabela "Lista de Usuários" | Colunas: Avatar+Nome, Email, Perfil (badge), Status (badge), Último Acesso, Ações (editar/excluir) |
| Botão "+ Novo Usuário" | Abre modal de cadastro |

### Perfis de Acesso Disponíveis

| Perfil | Badge |
|:-------|:------|
| Administrador | Azul escuro |
| Analista | Verde |
| Visualizador | Cinza |

---

### 7.2 Cadastrar Usuário (Modal)

### Componentes

![Cadastrar Usuário](/image/figma/usuario-cadastro.png)

| Elemento | Descrição |
|:---------|:----------|
| Campo "Nome Completo" | Input de texto obrigatório |
| Campo "Email" | Input de email obrigatório |
| Dropdown "Perfil de Acesso" | Seleção do perfil: Administrador, Analista ou Visualizador |
| Botão "Cancelar" | Fecha o modal sem salvar |
| Botão "Criar Usuário" | Salva o novo usuário |

### Regras de Negócio

- O usuário criado recebe um email com link de primeiro acesso
- O cadastro não inclui senha — ela será definida pelo próprio usuário no **Primeiro Acesso**
- Dados armazenados no PostgreSQL

---

### 7.3 Editar Usuário (Modal)

### Componentes

![Editar Usuário](/image/figma/usuario-editar.png)

| Elemento | Descrição |
|:---------|:----------|
| Campo "Nome Completo" | Pré-preenchido, editável |
| Campo "Email" | Pré-preenchido, editável |
| Dropdown "Perfil de Acesso" | Alteração de perfil |
| Dropdown "Status" | Alteração de status: Ativo / Inativo |
| Botão "Cancelar" | Fecha sem salvar |
| Botão "Salvar Alterações" | Persiste as alterações |

---

### 7.4 Excluir Usuário (Modal de Confirmação)

### Componentes

![Excluir Usuário](/image/figma/usuario-deletar.png)

| Elemento | Descrição |
|:---------|:----------|
| Ícone de alerta | Triângulo de aviso em vermelho |
| Mensagem de confirmação | Exibe o nome do usuário a ser excluído e aviso de que todos os dados associados serão removidos permanentemente |
| Botão "Cancelar" | Fecha sem excluir |
| Botão "Excluir Usuário" | Confirma e executa a exclusão permanente |

### Regras de Negócio

- A exclusão é permanente e irreversível
- Todos os dados associados ao usuário são removidos

---

## 8. Gestão de Termos

**Rota:** `/gestao-termos`  
**Acesso:** Perfil **Administrador** (restrito)

### Descrição

Gerenciamento dos termos de uso e políticas de privacidade exibidos no fluxo de Primeiro Acesso e reexibidos a usuários quando versões ativas são atualizadas.

---

### 8.1 Listagem de Termos

### Componentes

![Gestão de Termos](/image/figma/termos-1.png)
![Gestão de Termos - Histórico de Aceites](/image/figma/termos-2.png)

| Elemento | Descrição |
|:---------|:----------|
| Card "Termos Ativos" | Quantidade de termos publicados e ativos |
| Card "Rascunhos" | Quantidade de termos salvos como rascunho |
| Card "Inativos" | Quantidade de termos desativados |
| Card "Usuários que Aceitaram" | Total acumulado de aceites registrados |
| Abas de filtro | Todos / Ativos / Inativos / Rascunhos |
| Barra de busca | Busca por tipo ou descrição |
| Tabela de termos | Colunas: Tipo, Versão, Status (badge), Obrigatório (badge), Data Publicação, Descrição, Ações (visualizar / editar / excluir) |
| Painel "Histórico de Aceites Recentes" | Lista dos últimos usuários que aceitaram termos com email, versão aceita e data/hora |
| Botão "+ Novo Termo" | Abre modal de cadastro |

### Status dos Termos

| Status | Badge | Ações disponíveis |
|:-------|:------|:-----------------|
| Ativo | 🔵 Ativo | Visualizar, Editar |
| Inativo | ⚫ Inativo | Visualizar |
| Rascunho | 🟡 Rascunho | Visualizar, Editar, Excluir |

---

### 8.2 Cadastrar Termo (Modal)

### Componentes

![Cadastrar Termo](/image/figma/termos-cadastrar.png)

| Elemento | Descrição |
|:---------|:----------|
| Campo "Tipo" | Pré-selecionado: "Termos de Uso" ou "Política de Privacidade (LGPD)" |
| Campo "Versão" | Input de texto (ex: 1.0, 2.0) |
| Campo "Descrição" | Breve descrição das alterações |
| "Aceite do Termo" | Radio button: **Obrigatório** (usuário deve aceitar para continuar) ou **Opcional** (usuário pode recusar) |
| Campo "Conteúdo do Termo" | Textarea para o conteúdo completo do documento |
| Botão "Cancelar" | Fecha sem salvar |
| Botão "Salvar Rascunho" | Salva como rascunho (não exibido aos usuários ainda) |
| Botão "Publicar Termo" | Publica o termo como ativo (versão anterior é inativada automaticamente) |

---

### 8.3 Editar Termo (Modal)

Mesmo layout do modal de criação, com os campos pré-preenchidos. Disponível apenas para termos com status **Rascunho** ou **Ativo**.

![Editar Termo](/image/figma/termos-editar.png)

| Botão | Ação |
|:------|:-----|
| Cancelar | Fecha sem salvar |
| Salvar Alterações | Persiste as modificações |

---

### 8.4 Excluir Rascunho (Modal de Confirmação)

> ⚠️ Somente rascunhos podem ser excluídos. Termos ativos e inativos não possuem a opção de exclusão.

### Componentes

![Excluir Rascunho](/image/figma/termos-deletar.png)

| Elemento | Descrição |
|:---------|:----------|
| Ícone de alerta | Círculo de aviso em vermelho |
| Mensagem de confirmação | Exibe o tipo e versão do rascunho a ser excluído ("Esta ação não pode ser desfeita") |
| Botão "Cancelar" | Fecha sem excluir |
| Botão "Excluir" | Confirma e remove o rascunho permanentemente |

---

## 9. Meu Perfil

**Rota:** `/perfil`  
**Acesso:** Todos os perfis autenticados

### Descrição

Permite ao usuário visualizar e atualizar seus dados pessoais. Acessado via avatar/nome no canto superior direito da barra de navegação.

![Meu Perfil](/image/figma/perfil.png)

### Componentes

| Elemento | Descrição |
|:---------|:----------|
| Avatar com iniciais | Exibido com as iniciais do nome do usuário |
| Nome completo | Exibido abaixo do avatar |
| Email | Email do usuário |
| Badge de perfil | Tipo de acesso do usuário (ex: Administrador) |
| Campo "Nome Completo" | Editável |
| Campo "Email" | Editável |
| Campo "Telefone" | Editável |
| Campo "Cargo" | Editável |
| Campo "Departamento" | Editável |
| Campo "Perfil de Acesso" | Somente leitura (gerenciado pelo Administrador) |
| Info "Conta criada em" | Data de criação da conta |
| Info "Último acesso em" | Data e hora do último login registrado |
| Botão "Salvar Alterações" | Persiste as informações editadas |

### Regras de Negócio

- O campo **Perfil de Acesso** é somente leitura — alterações de perfil só podem ser feitas por um Administrador via Gestão de Usuários
- Dados salvos no PostgreSQL

---

## 📎 Observações Gerais

- **Sistema:** Zeus — Plataforma de Análise de Dados ANEEL
- **Empresa:** Tecsys do Brasil
- **Navegação:** Menu lateral fixo disponível em todas as telas autenticadas
- **Responsividade:** Interface compatível com navegadores modernos (RNF03)
- **LGPD:** Dados de usuários (credenciais, aceites, perfis) armazenados exclusivamente no PostgreSQL; dados operacionais da BDGD no MongoDB
- **Perfis de acesso existentes:** Administrador, Analista, Visualizador

---

*Última atualização: 17/03/2026*