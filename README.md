# <p align = "center">API 6º Semestre - BD 2026


<p align="center">
  <img src="docs/Zeus.png" alt="Descrição da imagem" width="400">
</p>


<p align="center">
  <a href=#problema>Contexto e Desafio</a> •
  <a href=#objetivo>Objetivo do Projeto</a> •
  <a href=#requisitos-funcionais-e-nao-funcionais>Requisitos Funcionais e Não Funcionais</a> •
  <a href=#backlog-do-produto>Backlog do Produto</a> •
  <a href=#date-sprint-backlog>Sprint Backlog</a> •
  <a href=#padroes-processos>Padrões de Processo</a> •
  <a href=#documentacao-tecnica>Documentação Técnica</a> •
  <a href=#integrantes-equipe>Integrantes da Equipe</a> •
  <a href=#tecnologias-utilizadas>Tecnologias Utilizadas</a> •
  <a href=#como-rodar-com-docker>Como Rodar com Docker</a> •
  <a href=#burndown>Evolução do Projeto (Burndown)</a> •
  <a href=#cronograma>Cronograma</a>

</p>

## :bulb: Contexto e Desafio <a id="problema"></a>

A Tecsys do Brasil, empresa parceira com atuação no setor de monitoramento de redes elétricas, possui produtos capazes de identificar falhas e vulnerabilidades na infraestrutura de distribuição de energia. Porém, apesar de dominar a tecnologia de monitoramento em campo, a empresa não dispõe de uma forma estruturada de processar e analisar os dados públicos disponibilizados pela ANEEL. Sem esse tratamento, identificar com precisão quais regiões do Brasil apresentam maior criticidade na rede de distribuição exige um esforço manual elevado — dificultando também a identificação de onde há maior potencial de aplicação dos seus produtos.

## :dart: Objetivo do Projeto <a id="objetivo"></a>

O objetivo do projeto é desenvolver uma plataforma que realize o tratamento e a análise dos dados provenientes da ANEEL, transformando informações brutas em indicadores acionáveis. Com isso, os analistas poderão identificar regiões prioritárias com base em critérios como qualidade de fornecimento, perdas de energia e vulnerabilidade da rede — subsidiando a equipe comercial com dados concretos para abordar novos mercados e oportunidades de aplicação do produto.

## Requisitos Funcionais e Não Funcionais<a id="requisitos-funcionais-e-nao-funcionais"></a>

<details>
<summary>Exibir Requisitos Funcionais e Não Funcionais</summary>

### Requisitos Funcionais

<details>
<summary>Exibir Requisitos Funcionais</summary><br>

| ID | Requisito | Descrição |
|:---|:---|:---|
| <a id="RF01">RF01</a> | _Pipeline ETL_ | O sistema deve realizar a extração, o tratamento e o carregamento (ETL) dos dados provenientes da base disponibilizada pela ANEEL, com registro de logs e controle de versionamento dos dados. |
| <a id="RF02">RF02</a> | _Dashboard de Redes de Distribuição_ | O sistema deve exibir dados referentes às estruturas das redes de distribuição (informações geográficas, elétricas e estruturais) via dashboards e relatórios interativos. |
| <a id="RF03">RF03</a> | _Relatórios de Redes de Distribuição_ | O sistema deve exibir indicadores e métricas de qualidade das redes elétricas (DEC, FEC e perdas de energia), permitindo filtragem por região e período. |
| <a id="RF04">RF04</a> | _Cálculo de TAM Físico_ | O sistema deve calcular e exibir os valores de TAM (Total Addressable Market) físico de instalação de sensores na rede elétrica, identificando o número máximo de pontos tecnicamente monitoráveis no Brasil. |
| <a id="RF05">RF05</a> | _Classificação por Criticidade com ML_ | O sistema deve agrupar regiões ou áreas da rede por nível de criticidade (alta, média, baixa), aplicando modelos de Machine Learning para apoiar a priorização de ações. |
| <a id="RF06">RF06</a> | _Ranking de Perdas de Energia_ | O sistema deve gerar um ranking de regiões com base nos indicadores de perdas de energia, utilizando modelos de regressão para projeção e ordenação das áreas mais críticas. |
| <a id="RF07">RF07</a> | _Gestão de Usuários e Perfis_ | O sistema deve permitir o cadastro de usuários com perfis distintos (Administrador e Analista), controlando o acesso a funcionalidades e dados conforme o perfil. |
| <a id="RF08">RF08</a> | _Cálculo de SAM_ | O sistema deve calcular e exibir os valores de SAM, cruzando o TAM com critérios técnicos, regulatórios e de viabilidade operacional. |
| <a id="RF09">RF09</a> | _Mapa de Calor Geográfico_ | O sistema deve exibir um mapa de calor (heatmap) geográfico indicando o nível de criticidade da rede elétrica por região, com suporte a filtros dinâmicos por indicador. |
| <a id="RF10">RF10</a> | _Conformidade com LGPD_ | O sistema deve garantir conformidade com a LGPD: coleta de consentimento explícito, anonimização de dados pessoais, política de retenção e exclusão, e geração de relatório de tratamento de dados (ROPA simplificado para fins acadêmicos). |

</details>

### Requisitos Não Funcionais

<details>
<summary>Exibir Requisitos não Funcionais</summary><br>

| ID | Requisito | Descrição |
|:---|:---|:---|
| <a id="RNF01">RNF01</a> | _Performance de Consultas ao Banco_ | As consultas críticas ao banco de dados — relacional (dados sensíveis) e MongoDB (dados da ANEEL) — devem apresentar desempenho adequado para uso fluido da aplicação, com uso de paginação e índices básicos.|
| <a id="RNF02">RNF02</a> | _Inicialização e Estabilidade da Aplicação_ | A aplicação web deve inicializar corretamente e operar de forma estável durante sessões contínuas de uso, sem travamentos ou erros inesperados. |
| <a id="RNF03">RNF03</a> | _Responsividade e Compatibilidade_ | A interface deve ser responsiva, garantindo compatibilidade e boa experiência em navegadores modernos. |
| <a id="RNF04">RNF04</a> | _Métricas de Desempenho de ML_ | O desempenho do modelo de machine learning treinado deve ser documentado com as métricas adequadas ao tipo de tarefa: Silhouette Score para clustering, RMSE para regressão e F1-Score para classificação. |
| <a id="RNF05">RNF05</a> | _Consistência Pós-Carga Manual_ | Sempre que houver nova carga de dados os indicadores (DEC, FEC e perdas) devem ser recalculados, com exibição da data/hora da última carga e identificação da versão do lote utilizado. |

</details>
</details>

<a id=""></a>

## :date: Backlog do Produto <a id="backlog-do-produto"></a>
<details>

<summary>Mostrar Backlog do Produto</summary>

<br>

| ID | Rank | Prioridade | User Story | Sprint | Requisitos Relacionados |
|:---|:---|:---|:---|:---|:---|
| US01 | 01 | Highest | Como analista de dados, quero acessar relatórios de estruturas das redes de distribuição, para identificar características geográficas, elétricas e estruturais da infraestrutura monitorada. | 01 | [RF01](#RF01), [RF02](#RF02) |
| US02 | 02 | Highest | Como analista de dados, quero que o sistema exponha dados de qualidade (DEC, FEC, perdas), para avaliar o desempenho da rede elétrica por região e período. | 01 | [RF01](#RF01), [RF03](#RF03) |
| US03 | 03 | High | Como usuário, quero que o sistema responda rapidamente às minhas consultas, sem travamentos durante o uso. | 01 | [RNF01](#RNF01), [RNF02](#RNF02) |
| US04 | 04 | Medium | Como usuário, quero acessar o sistema por qualquer navegador moderno com boa experiência visual. | 01 | [RNF03](#RNF03) |
| US05 | 01 | Highest | Como analista de dados, quero agrupar regiões por nível de criticidade, para que a equipe comercial possa priorizar abordagens nas áreas com maior potencial de aplicação do produto. | 02 | [RF05](#RF05) |
| US06 | 02 | Highest | Como analista comercial, quero calcular o TAM físico de instalação de sensores, para dimensionar o universo máximo de pontos monitoráveis no Brasil. | 02 | [RF04](#RF04) |
| US07 | 03 | High | Como analista de dados, quero um ranking de regiões por perdas de energia, para identificar as áreas mais críticas e subsidiar decisões técnicas e comerciais. | 02 | [RF06](#RF06) |
| US08 | 04 | High | Como administrador, quero cadastrar e gerenciar usuários com perfis distintos, para controlar o acesso às funcionalidades conforme o papel de cada usuário. | 02 | [RF07](#RF07) |
| US09 | 05 | Medium | Como analista de dados, quero que os modelos de ML tenham desempenho documentado e métricas validadas, para garantir a confiabilidade dos resultados gerados pelo sistema. | 02 | [RNF04](#RNF04) |
| US10 | 01 | Highest | Como analista comercial, quero um indicador de SAM, para identificar o mercado acessível do produto por região com base em critérios técnicos e regulatórios. | 03 | [RF08](#RF08) |
| US11 | 02 | Highest | Como analista comercial, quero uma visualização geográfica (mapa de calor), para identificar visualmente as regiões prioritárias de atuação comercial. | 03 | [RF09](#RF09) |
| US12 | 03 | High | Como usuário, quero controle e transparência sobre meus dados pessoais (LGPD), para garantir que minhas informações sejam tratadas de forma segura e conforme a legislação. | 03 | [RF07](#RF07), [RF10](#RF10) |
| US13 | 04 | Medium | Como analista de dados, quero que os indicadores sejam recalculados automaticamente após cada nova carga de dados, para garantir que as análises sempre reflitam as informações mais atualizadas. | 03 | [RNF05](#RNF05) |
</details>

## :date: Sprint Backlog <a id="date-sprint-backlog"></a>
<details>

<summary>Mostrar Spring Backlog</summary>

### Sprint 1

[Ver documentação da Sprint 1](docs/SPRINT1.md)


### Sprint 2

[Ver documentação da Sprint 2](docs/SPRINT2.md)


### Sprint 3

[Ver documentação da Sprint 3](docs/SPRINT3.md)


</details>

<br>

## :calendar: <a id="cronograma"> Cronograma 📅 </a>

| Sprint  | Nome | Data inicio  | Data Fim | Status |
| --- | -------------------------- | --------| ----- |:---:|
| --- | KickOff                    | 02/03   | 06/03 | Ok  |
| --- | Planejamento               | 09/03   | 13/13 | Ok  |
|  1  | Sprint 1                   | 16/03   | 05/04 |     |
|  2  | Sprint review / Planning   | 06/04   | 10/04 |     |
|  3  | Sprint 2                   | 13/04   | 03/05 |     |
|  4  | Sprint review / Planning   | 04/05   | 08/05 |     |
|  5  | Sprint 3                   | 11/05   | 31/05 |     |
|  6  | Sprint review              | 01/06   | 05/06 |     |
|  7  | Feira de Soluções          | 11/06   |       |     |
|  8  | Apresentações TGs          | 15/06   | 19/06 |     |

<br>

## :mortar_board: Integrantes da Equipe <a id="integrantes-equipe"></a>

| *Nome*                   | *Função*            | *LinkedIn*                                                  |
|:------------------:|:-----------------:|:---------------------------------------:|
| Vinicius Monteiro | Product Owner     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/viniciusvasm/ ) |
| Cesar Pelogia | Scrum Master  | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/ ) |
| Alexandre Jonas | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/alexandre-jonas-de-souza-fonseca-989920181/) |
| Eliézer Lopes     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/eli%C3%A9zer-lopes/) |
| Lucas Henrique | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/lucashenriqueco/) |
| Gabriel Souza | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gabriel-alves-de-souza-5b7747267/) |
| Gustavo Robert     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gustavo-robert/) |
| Vitor Morais       | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/vitor-faria-morais-330b19204/) |

</br>

## Padrões de Processo <a id="padroes-processos"></a>
[Documentação Geral](docs/DOCUMENTACAO.md)  
[Padrões de Commits e Branches](docs/PADROES-COMMITS-BRANCHES.md)  
[Rastreio de Issues](docs/RASTREIO-ISSUES.md)

</br>

## Documentação Técnica <a id="documentacao-tecnica"></a>

[Prototipagem](docs/FLUXO-FIGMA.md)  
[Como rodar o projeto](docs/COMO-RODAR-PROJETO.md)

</br>

## Evolução do Projeto (Burndown)<a id="burndown"></a>

<img src="burndown/src/main/resources/static/burndown.png?v=9ea14aec912b12134ba7eaeb2b9e3ff8cc534998">

</br>

## 🛠️ Tecnologias Utilizadas <a id="tecnologias-utilizadas"></a>

Esta solução é composta por uma aplicação principal e por um módulo de apoio para acompanhamento da evolução do projeto (Burndown).

### 🖥️ Frontend
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)

### ⚙️ Backend
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

### 🗄️ Banco de Dados
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

### 📊 Burndown (Módulo de Apoio)
[![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](https://www.java.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![GitHub API](https://img.shields.io/badge/GitHub_API-181717?style=for-the-badge&logo=github&logoColor=white)](https://docs.github.com/en/rest)

### 💬 Comunicação
[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://slack.com/)


<br>

## Burndown Automatico

Guia completo de uso, execução local e CI:

- `burndown/README.md`
