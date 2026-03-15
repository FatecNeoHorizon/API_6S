# Sprint 3 — Visão Estratégica e Conformidade

[Voltar ao README principal](../README.md#date-sprint-backlog)

> **Período:** 11/05/2026 → 31/05/2026  
> **Status:** ⏳ Aguardando

---

## 🎯 Objetivo da Sprint

Entregar a visão estratégica completa do produto — consolidando o SAM, o mapa de calor geográfico e a conformidade com a LGPD, fechando o ciclo de análise que vai dos dados brutos da BDGD/ANEEL até a priorização comercial de regiões para a Tecsys, com destaque para oportunidades na malha de transmissão.

---

## ✅ MVC da Sprint — Entregas

### 🟢 Mínimo Comprometido
O que a equipe se compromete a entregar obrigatoriamente até o fim da sprint.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Mapa de calor geográfico com Leaflet | ⬜ |
| 2 | Cálculo e exibição do SAM | ⬜ |
| 3 | Conformidade com LGPD | ⬜ |

### 🔵 Entregas Adicionais
O que será entregue além do mínimo, caso o tempo e contexto permitissem.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Recálculo automático de indicadores após nova carga de dados | ⬜ |

---

## 📋 User Stories e Requisitos

| User Story | Descrição | Requisitos | Prioridade |
|:-----------|:----------|:----------:|:----------:|
| US10 | Como analista, quero um indicador de SAM por região. | RF08 | 🔴 Highest |
| US11 | Como analista comercial, quero uma visualização geográfica para priorizar regiões de abordagem comercial. | RF09 | 🔴 Highest |
| US12 | Como usuário, quero controle e transparência sobre meus dados pessoais (LGPD). | RF07, RF10 | 🟠 High |
| US13 | Como analista, quero que os indicadores sejam recalculados automaticamente após cada nova carga de dados. | RNF05 | 🟡 Medium |

---

## 🏗️ Arquitetura e Decisões Técnicas

### Integração do Leaflet com React para o mapa de calor

O mapa de calor será implementado com **Leaflet** integrado ao React via
`react-leaflet`, com o plugin `leaflet.heat` para renderização do heatmap.

A escolha do Leaflet se justifica por:
- Curva de aprendizado baixa em relação a alternativas como Google Maps ou Mapbox
- Suporte nativo a heatmap via plugin oficial
- Open source e sem custo de API
- Integração limpa com `react-leaflet` no frontend React

**Estratégia de agregação para o mapa:**  
O layer `CONJ` (82 polígonos MultiPolygon) é o nível ideal de agregação para
o heatmap. Em vez de renderizar milhões de pontos individuais, o mapa exibe
82 zonas geográficas com a criticidade média de cada conjunto — performance
adequada no navegador sem comprometer a legibilidade da informação.

O mapa suporta **filtro por tipo de rede** (transmissão/distribuição) e por
indicador (DEC, FEC, perdas), usando o atributo `tipo_rede` definido na Sprint 1.

### Cálculo do SAM

O SAM é obtido aplicando filtros sobre o TAM físico calculado na Sprint 2.
O campo `ARE_LOC` da BDGD é o critério operacional central:

- **Técnicos:** pontos cuja infraestrutura é compatível com o sensor da Tecsys
- **Regulatórios:** distribuidoras sob metas obrigatórias de DEC/FEC da ANEEL
- **Operacionais:** `ARE_LOC != urbano denso` — priorização da malha de
  transmissão e pontos periurbanos/rurais onde a logística de instalação é viável

> O SAM fecha o ciclo: TAM responde *"quantos pontos existem?"*,
> SAM responde *"quantos pontos a Tecsys pode realisticamente atender?"*.
> Para a Tecsys, a resposta está predominantemente em `SUB`, `UNTRAT` e
> `UNTRMT` com `ARE_LOC` rural ou periurbano.

### Conformidade com LGPD

A adequação à LGPD será implementada sobre a camada de dados sensíveis
já isolada no PostgreSQL desde a Sprint 1. O sistema coleta apenas os dados
estritamente necessários: **nome, e-mail, senha e cargo**.

**Anonimização e proteção**
- Senha armazenada com hash **bcrypt** — nunca em texto plano
- E-mail e nome mascarados em logs do sistema e relatórios exportados
- Cargo mantido apenas para controle de perfil de acesso

**Consentimento explícito**
- Aceite obrigatório nos termos de uso no cadastro, conforme Art. 8º da LGPD

**Política de retenção e exclusão**
- Dados mantidos enquanto a conta estiver ativa
- Exclusão completa em até 30 dias após solicitação, conforme Art. 18 da LGPD
- Logs de acesso retidos por 90 dias para auditoria

**ROPA simplificado**
- Relatório de tratamento de dados gerado para fins acadêmicos

> A separação entre PostgreSQL (dados sensíveis) e MongoDB (dados públicos BDGD),
> definida na Sprint 1, foi o principal fator arquitetural que simplificou
> a implementação da conformidade com a LGPD nesta sprint.

### Recálculo automático de indicadores

Após cada nova carga de dados, o sistema dispara automaticamente o recálculo
dos indicadores DEC, FEC e perdas. A interface exibe a data/hora da última
carga e o identificador da versão do lote, garantindo rastreabilidade (RNF05).

---

*Última atualização: 16/03/2026*