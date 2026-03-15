# Sprint 1 — Relatórios e Estrutura de Dados

[Voltar ao README principal](../README.md#date-sprint-backlog)

> **Período:** 16/03/2026 → 05/04/2026  
> **Status:** 🔄 Em andamento

---

## 🎯 Objetivo da Sprint

Estabelecer a base de dados e visibilidade da rede elétrica — construindo o pipeline ETL sobre os dados da BDGD/ANEEL e expondo os primeiros indicadores de qualidade (DEC, FEC e perdas) em uma interface funcional e responsiva, contemplando tanto a malha de transmissão quanto a de distribuição.

---

## ✅ MVC da Sprint — Entregas

### 🟢 Mínimo Comprometido
O que a equipe se compromete a entregar obrigatoriamente até o fim da sprint.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Pipeline ETL funcional com os layers prioritários da BDGD | ⬜ |
| 2 | Exposição dos indicadores DEC, FEC e perdas agregados por região | ⬜ |

### 🔵 Entregas Adicionais
O que será entregue além do mínimo, caso o tempo e contexto permitissem.

| # | Funcionalidade | Status |
|:--|:--------------|:------:|
| 1 | Dashboard interativo com filtros por região e tipo de rede | ⬜ |
| 2 | Interface responsiva e compatível com navegadores modernos | ⬜ |

---

## 📋 User Stories e Requisitos

| User Story | Descrição | Requisitos | Prioridade |
|:-----------|:----------|:----------:|:----------:|
| US01 | Como analista, quero acessar relatórios de estruturas das redes de distribuição. | RF01, RF02 | 🔴 Highest |
| US02 | Como analista, quero que o sistema exponha dados de qualidade (DEC, FEC, perdas). | RF01, RF03 | 🔴 Highest |
| US03 | Como usuário, quero que o sistema responda rapidamente, sem travamentos. | RNF01, RNF02 | 🟠 High |
| US04 | Como usuário, quero acessar o sistema por qualquer navegador moderno. | RNF03 | 🟡 Medium |

---

## 🏗️ Arquitetura e Decisões Técnicas

### Separação de responsabilidades entre os bancos de dados

A arquitetura de dados foi projetada com dois bancos de dados com responsabilidades distintas e complementares:

**PostgreSQL — dados sensíveis**  
Responsável pelo armazenamento de dados que exigem conformidade com a LGPD:
credenciais de usuários, perfis de acesso e qualquer informação pessoal identificável.
A escolha garante controle transacional, integridade referencial e facilidade
de auditoria — requisitos essenciais para atender à legislação.

**MongoDB — dados públicos (BDGD)**  
Responsável pelo armazenamento dos dados da BDGD/ANEEL.
Por serem dados públicos, não há restrições de privacidade. A escolha se justifica
pela facilidade de ingestão de grandes volumes de dados semiestruturados e pelo
suporte nativo a GeoJSON — necessário para os layers com geometria da BDGD.

> Essa separação garante que dados sensíveis nunca trafeguem ou
> residam no mesmo ambiente que os dados operacionais públicos,
> simplificando a conformidade com a LGPD e reduzindo a superfície de risco.

### Layers da BDGD e estratégia de ingestão

A BDGD é composta por 43 layers. Nesta sprint, são ingeridos apenas os layers
de alta prioridade para os indicadores e estrutura da rede:

**Layers obrigatórios na Sprint 1:**
- `SUB` — subestações com geometria
- `UNTRAT` — transformadores AT com perdas e energia mensal
- `UNTRMT` — transformadores MT com geometria e perdas
- `SSDAT` — segmentos de rede AT com geometria
- `CTMT` — circuitos MT com indicadores de perdas mensais
- `UCBT_tab` — consumidores BT com DIC/FIC mensais
- `UCMT_tab` — consumidores MT com DIC/FIC mensais
- `UCAT_tab` — consumidores AT com DIC/FIC mensais
- `CONJ` — conjuntos geográficos — nível de agregação para o heatmap

**Atenção especial:**
`UCBT_tab` tem 3M de registros (1.4GB em memória). A ingestão deve ser feita
em chunks de 100.000 linhas. Índice composto `{DIST, MUN, CONJ}` deve ser
criado antes de qualquer consulta analítica.

### Cálculo dos indicadores DEC e FEC

DEC e FEC são calculados a partir dos campos `DIC_01..DIC_12` e `FIC_01..FIC_12`
presentes nas tabelas de consumidores (`UCBT_tab`, `UCMT_tab`, `UCAT_tab`).
O ETL agrega esses valores por `MUN` (município) e `CONJ` (conjunto elétrico)
— nunca expondo dados individuais por UC.

### Perdas de energia

Três granularidades disponíveis na BDGD:
- **Por circuito MT:** `CTMT.PERD_MED` — perda média percentual do circuito. Feature principal para o ranking.
- **Por transformador MT:** `EQTRMT.PER_TOT` — perda total por transformador.
- **Por transformador AT:** diferença entre `UNTRAT.ENES_XX` (energia secundário) e `UNTRAT.ENET_XX` (energia terciário).

### Estrutura da API com FastAPI

O backend será construído com FastAPI por três razões principais:
a exposição de dados via API REST para o frontend React, a integração natural
com bibliotecas de ML (scikit-learn, pandas/geopandas) e a geração automática de
documentação Swagger — facilitando a comunicação com o cliente e a validação
das rotas durante as sprint reviews.

### Desenho do pipeline ETL

O pipeline segue o fluxo extração → transformação → carga, com registro de logs
em cada etapa e controle de versionamento por lote. Cada carga recebe um
identificador de versão, permitindo rastrear qual conjunto de dados alimentou
cada indicador exibido na interface.

O atributo `tipo_rede` (transmissão/distribuição) é derivado da tensão nominal
de cada layer e preservado como campo indexável no MongoDB para uso nas sprints seguintes.
O campo `ARE_LOC` (área de localização: urbana/rural/periurbana), presente em
vários layers, é preservado para alimentar o filtro operacional do SAM na Sprint 3.

---

*Última atualização: 16/03/2026*