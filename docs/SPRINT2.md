# Sprint 2 — Inteligência Comercial e Análise de Mercado

[Voltar ao README principal](../README.md#date-sprint-backlog)

> **Período:** 13/04/2026 → 03/05/2026  
> **Status:** ⏳ Aguardando

---

## 🎯 Objetivo da Sprint

Transformar dados em inteligência comercial — aplicando modelos de Machine Learning para classificar regiões por criticidade, gerar rankings de perdas e calcular o TAM físico, entregando à Tecsys métricas concretas para embasar decisões de mercado, com foco prioritário na malha de transmissão.

---

## ✅ MVC da Sprint — Entregas

### 🟢 Mínimo Comprometido
O que a equipe se compromete a entregar obrigatoriamente até o fim da sprint.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Classificação de regiões por criticidade com ML | ⬜ |
| 2 | Ranking de regiões por perdas de energia | ⬜ |
| 3 | Cálculo e exibição do TAM físico | ⬜ |

### 🔵 Entregas Adicionais
O que será entregue além do mínimo, caso o tempo e contexto permitissem.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Gestão de usuários com perfis distintos (Administrador e Analista) | ⬜ |
| 2 | Métricas de desempenho dos modelos de ML documentadas | ⬜ |

---

## 📋 User Stories e Requisitos

| User Story | Descrição | Requisitos | Prioridade |
|:-----------|:----------|:----------:|:----------:|
| US05 | Como analista, quero agrupar regiões por nível de criticidade. | RF05 | 🔴 Highest |
| US06 | Como analista, quero calcular o TAM físico de instalação de sensores. | RF04 | 🔴 Highest |
| US07 | Como analista, quero um ranking de regiões por perdas de energia. | RF06 | 🟠 High |
| US08 | Como administrador, quero cadastrar e gerenciar usuários com perfis distintos. | RF07 | 🟠 High |
| US09 | Como analista, quero que os modelos de ML tenham desempenho documentado e métricas validadas. | RNF04 | 🟡 Medium |

---

## 🏗️ Arquitetura e Decisões Técnicas

### Features para o modelo de ML

Os dados da BDGD permitem construir features concretas por região (agregadas por `CONJ`):

| Feature | Layer de origem | Campo | Descrição |
|:--------|:---------------|:------|:----------|
| DEC médio | UCBT_tab + UCMT_tab | DIC_01..12 (média anual) | Duração média de interrupções |
| FEC médio | UCBT_tab + UCMT_tab | FIC_01..12 (média anual) | Frequência média de interrupções |
| Perda média do circuito | CTMT | PERD_MED | Perda percentual média |
| Perda nos transformadores MT | EQTRMT | PER_TOT (média por CONJ) | Perdas nos transformadores |

### Modelo de clustering para classificação de criticidade

Para classificar regiões por nível de criticidade (alta, média, baixa), foi
adotado o algoritmo **K-Means** com 3 clusters. A escolha se justifica por:

- Funciona bem com as features tabulares disponíveis (DEC, FEC, perdas por CONJ)
- Implementação direta via scikit-learn, com documentação ampla e fácil validação acadêmica
- Número fixo de clusters alinhado ao requisito RF05 (baixa/média/alta)

O modelo é aplicado separadamente para transmissão e distribuição, usando o
atributo `tipo_rede` definido na Sprint 1. O desempenho é avaliado com **Silhouette Score** (RNF04).

### Modelo de regressão para ranking de perdas

Para o ranking de regiões por perdas, foi adotado o **Random Forest Regressor**.
A feature principal é `CTMT.PERD_MED` (perda média do circuito MT), enriquecida
com `EQTRMT.PER_TOT` agregado por `CONJ`. O ranking é gerado separadamente
para transmissão e distribuição. Avaliado com **RMSE** (RNF04).

### Cálculo do TAM físico

Com base nos dados da BDGD, o TAM físico é calculado contando os pontos
monitoráveis por tipo de rede:

**Transmissão (foco principal da Tecsys):**
- `SUB` — subestações com geometria
- `UNTRAT` — transformadores AT
- `SSDAT` — trechos de rede AT (pontos de medição potenciais)
- `UNSEAT` — chaves de manobra AT

**Distribuição (mercado secundário):**
- `UNTRMT` — transformadores MT

O campo `ARE_LOC` é o critério operacional para separar pontos viáveis de
difícil acesso. Validar os valores de `ARE_LOC` com a Tecsys antes da sprint review.

### Controle de acesso com JWT

A autenticação será implementada com **JWT (JSON Web Token)** via `python-jose`
integrado ao FastAPI. Credenciais armazenadas no PostgreSQL com senha em bcrypt.

---

*Última atualização: 16/03/2026*